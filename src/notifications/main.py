import json
import logging
import asyncio
from typing import Dict, Any
from infrastructure.adapters.dynamodb_record_processor import DynamoDBRecordProcessor
from infrastructure.adapters.sns_notification_sender import SNSNotificationSender
from infrastructure.adapters.sns_contact_manager import SNSContactManager
from application.use_cases.subscription_notifications import SubscriptionNotificationUseCase
from application.use_cases.user_profile_notifications import UserProfileNotificationUseCase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class NotificationService:
    """Main notification service orchestrator"""
    
    def __init__(self):
        # Initialize adapters
        self.record_processor = DynamoDBRecordProcessor()
        self.notification_sender = SNSNotificationSender()
        self.contact_manager = SNSContactManager()
        
        # Initialize use cases
        self.subscription_use_case = SubscriptionNotificationUseCase(
            self.notification_sender
        )
        self.user_profile_use_case = UserProfileNotificationUseCase(
            self.notification_sender,
            self.contact_manager
        )
    
    async def process_dynamodb_records(self, records: list) -> Dict[str, Any]:
        """
        Process list of DynamoDB Stream records
        
        Args:
            records: List of DynamoDB Stream records from Lambda event
            
        Returns:
            Dict[str, Any]: Processing results summary
        """
        results = {
            "processed": 0,
            "skipped": 0,
            "errors": 0,
            "details": []
        }
        
        for i, record in enumerate(records):
            try:
                logger.info(f"=== Processing record {i+1}/{len(records)} ===")
                
                # Parse the DynamoDB Stream record
                stream_record = self.record_processor.parse_stream_record(record)
                logger.info(f"Parsed record: ID={stream_record.eventID}, event={stream_record.eventName}")
                
                # Transform to ProcessedRecord
                processed_record = self.record_processor.transform_record(stream_record)
                if not processed_record:
                    logger.warning(f"Could not transform record: {stream_record.eventID}")
                    results["skipped"] += 1
                    continue
                
                logger.info(f"Transformed record: PK={processed_record.pk}, SK={processed_record.sk}")
                
                # Check if record should be processed
                if not self.record_processor.should_process_record(processed_record):
                    logger.info(f"Record should not be processed: {processed_record.pk}/{processed_record.sk}")
                    results["skipped"] += 1
                    continue
                
                logger.info(f"Record will be processed: {processed_record.pk}/{processed_record.sk}")
                
                # Route to appropriate use case
                success = await self._route_to_use_case(processed_record)
                logger.info(f"Use case processing result: {success}")
                
                if success:
                    results["processed"] += 1
                    results["details"].append({
                        "record_id": stream_record.eventID,
                        "pk": processed_record.pk,
                        "sk": processed_record.sk,
                        "status": "success"
                    })
                else:
                    results["errors"] += 1
                    results["details"].append({
                        "record_id": stream_record.eventID,
                        "pk": processed_record.pk,
                        "sk": processed_record.sk,
                        "status": "error"
                    })
                
                logger.info(f"=== Completed record {i+1}/{len(records)} ===")
                
            except Exception as e:
                logger.error(f"=== ERROR processing record {i+1}/{len(records)} ===")
                logger.error(f"Error: {str(e)}", exc_info=True)
                results["errors"] += 1
                results["details"].append({
                    "record_id": record.get("eventID", "unknown"),
                    "status": "error",
                    "error": str(e)
                })
        
        return results
    
    async def _route_to_use_case(self, processed_record) -> bool:
        """
        Route processed record to appropriate use case
        
        Args:
            processed_record: ProcessedRecord to route
            
        Returns:
            bool: True if processing was successful
        """
        try:
            if processed_record.is_user_subscription:
                logger.info(f"Routing to subscription use case: {processed_record.pk}/{processed_record.sk}")
                logger.info(f"Record data: {processed_record.data}")
                result = await self.subscription_use_case.handle_subscription_change(processed_record)
                logger.info(f"Subscription use case result: {result}")
                return result
            
            elif processed_record.is_user_profile:
                logger.info(f"Routing to user profile use case: {processed_record.pk}/{processed_record.sk}")
                logger.info(f"Record data: {processed_record.data}")
                result = await self.user_profile_use_case.handle_user_profile_creation(processed_record)
                logger.info(f"User profile use case result: {result}")
                return result
            
            else:
                logger.warning(f"No use case for record: {processed_record.pk}/{processed_record.sk}")
                return False
                
        except Exception as e:
            logger.error(f"Error in use case routing for {processed_record.pk}/{processed_record.sk}: {str(e)}", exc_info=True)
            return False


# Global service instance
notification_service = NotificationService()


def lambda_handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """
    AWS Lambda handler for DynamoDB Stream events
    
    Args:
        event: Lambda event containing DynamoDB Stream records
        context: Lambda context object
        
    Returns:
        Dict[str, Any]: Processing results
    """
    # Basic event logging
    print(f"Lambda triggered with event: {json.dumps(event, default=str)}")
    logger.info("=== LAMBDA HANDLER STARTED ===")
    
    try:
        # Extract DynamoDB records from event
        records = event.get('Records', [])
        logger.info(f"Received {len(records)} DynamoDB Stream records")
        
        if not records:
            logger.info("No records to process")
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "No records to process"})
            }
        
        # Log each record for debugging
        for i, record in enumerate(records):
            logger.info(f"Record {i+1}: eventName={record.get('eventName')}, "
                       f"PK={record.get('dynamodb', {}).get('Keys', {}).get('PK')}, "
                       f"SK={record.get('dynamodb', {}).get('Keys', {}).get('SK')}")
        
        # Process records asynchronously
        logger.info("Starting async processing...")
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(
                notification_service.process_dynamodb_records(records)
            )
            logger.info(f"Async processing completed with results: {results}")
        except Exception as async_error:
            logger.error(f"Error in async processing: {str(async_error)}", exc_info=True)
            raise
        finally:
            loop.close()
        
        logger.info("=== LAMBDA HANDLER COMPLETED SUCCESSFULLY ===")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Records processed successfully",
                "results": results
            }, default=str)
        }
        
    except Exception as e:
        logger.error(f"=== LAMBDA HANDLER ERROR ===")
        logger.error(f"Error type: {type(e).__name__}")
        logger.error(f"Error message: {str(e)}")
        logger.error(f"Full traceback:", exc_info=True)
        
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Internal server error",
                "error_type": type(e).__name__,
                "message": str(e)
            })
        }