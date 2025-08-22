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
        
        for record in records:
            try:
                # Parse the DynamoDB Stream record
                stream_record = self.record_processor.parse_stream_record(record)
                logger.info(f"Processing record: {stream_record.eventID} - {stream_record.eventName}")
                
                # Transform to ProcessedRecord
                processed_record = self.record_processor.transform_record(stream_record)
                if not processed_record:
                    logger.warning(f"Could not transform record: {stream_record.eventID}")
                    results["skipped"] += 1
                    continue
                
                # Check if record should be processed
                if not self.record_processor.should_process_record(processed_record):
                    logger.info(f"Skipping record: {processed_record.pk}/{processed_record.sk}")
                    results["skipped"] += 1
                    continue
                
                # Route to appropriate use case
                success = await self._route_to_use_case(processed_record)
                
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
                
            except Exception as e:
                logger.error(f"Error processing record: {str(e)}")
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
                return await self.subscription_use_case.handle_subscription_change(processed_record)
            
            elif processed_record.is_user_profile:
                logger.info(f"Routing to user profile use case: {processed_record.pk}/{processed_record.sk}")
                return await self.user_profile_use_case.handle_user_profile_creation(processed_record)
            
            else:
                logger.warning(f"No use case for record: {processed_record.pk}/{processed_record.sk}")
                return False
                
        except Exception as e:
            logger.error(f"Error in use case routing: {str(e)}")
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
    print(event)

    logger.info(f"Received DynamoDB Stream event with {len(event.get('Records', []))} records")
    try:
        # Extract DynamoDB records from event
        records = event.get('Records', [])
        
        if not records:
            logger.info("No records to process")
            return {
                "statusCode": 200,
                "body": json.dumps({"message": "No records to process"})
            }
        
        # Process records asynchronously
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            results = loop.run_until_complete(
                notification_service.process_dynamodb_records(records)
            )
        finally:
            loop.close()
        
        logger.info(f"Processing complete: {results}")
        
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Records processed successfully",
                "results": results
            })
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in lambda handler: {str(e)}")
        return {
            "statusCode": 500,
            "body": json.dumps({
                "error": "Internal server error",
                "message": str(e)
            })
        }