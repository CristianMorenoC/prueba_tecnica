import logging
from typing import Dict, Any, Optional
from application.ports.record_processor import RecordProcessorPort
from domain.models.dynamodb_record import (
    DynamoDBStreamRecord, 
    ProcessedRecord,
    EventName
)

logger = logging.getLogger(__name__)


class DynamoDBRecordProcessor(RecordProcessorPort):
    """DynamoDB Stream record processor implementation"""
    
    def parse_stream_record(self, record: dict) -> DynamoDBStreamRecord:
        """
        Parse raw DynamoDB Stream record from Lambda event
        
        Args:
            record: Raw record from DynamoDB Stream event
            
        Returns:
            DynamoDBStreamRecord: Parsed record
        """
        try:
            return DynamoDBStreamRecord(**record)
        except Exception as e:
            logger.error(f"Error parsing DynamoDB Stream record: {str(e)}")
            logger.error(f"Record data: {record}")
            raise
    
    def transform_record(self, stream_record: DynamoDBStreamRecord) -> Optional[ProcessedRecord]:
        """
        Transform DynamoDB Stream record to ProcessedRecord
        
        Args:
            stream_record: Parsed DynamoDB Stream record
            
        Returns:
            Optional[ProcessedRecord]: Transformed record or None if cannot be processed
        """
        try:
            # Get the appropriate image based on event type
            image = None
            if stream_record.eventName == EventName.REMOVE:
                image = stream_record.old_image
            else:
                image = stream_record.new_image
            
            if not image:
                logger.warning(f"No image available for record {stream_record.eventID}")
                return None
            
            # Extract PK and SK
            pk = self._extract_attribute_value(image.PK)
            sk = self._extract_attribute_value(image.SK)
            
            if not pk or not sk:
                logger.warning(f"Missing PK or SK in record {stream_record.eventID}")
                return None
            
            # Transform all attributes to a flat dictionary
            data = self._transform_dynamodb_image_to_dict(image)
            
            return ProcessedRecord(
                pk=pk,
                sk=sk,
                event_name=stream_record.eventName,
                data=data
            )
            
        except Exception as e:
            logger.error(f"Error transforming DynamoDB record: {str(e)}")
            return None
    
    def should_process_record(self, processed_record: ProcessedRecord) -> bool:
        """
        Determine if record should be processed for notifications
        
        Args:
            processed_record: ProcessedRecord to evaluate
            
        Returns:
            bool: True if record should be processed
        """
        # Process USER# records with SUB# (subscriptions) or PROFILE (user profiles)
        if processed_record.is_user_subscription:
            logger.info(f"Processing subscription record: {processed_record.pk}/{processed_record.sk}")
            return True
        
        if processed_record.is_user_profile and processed_record.event_name == EventName.INSERT:
            logger.info(f"Processing user profile creation: {processed_record.pk}/{processed_record.sk}")
            return True
        
        logger.debug(f"Skipping record: {processed_record.pk}/{processed_record.sk}")
        return False
    
    def _extract_attribute_value(self, attribute: Optional[Dict[str, Any]]) -> Optional[str]:
        """
        Extract value from DynamoDB attribute
        
        Args:
            attribute: DynamoDB attribute dictionary
            
        Returns:
            Optional[str]: Extracted string value
        """
        if not attribute:
            return None
        
        # DynamoDB attributes have type indicators like {'S': 'value'} for strings
        if 'S' in attribute:
            return attribute['S']
        elif 'N' in attribute:
            return attribute['N']
        elif 'B' in attribute:
            return attribute['B']
        elif 'SS' in attribute:
            return ','.join(attribute['SS'])
        elif 'NS' in attribute:
            return ','.join(attribute['NS'])
        elif 'BS' in attribute:
            return ','.join(attribute['BS'])
        elif 'M' in attribute:
            return str(attribute['M'])
        elif 'L' in attribute:
            return str(attribute['L'])
        elif 'NULL' in attribute:
            # Handle DynamoDB NULL values
            return None if attribute['NULL'] else None
        elif 'BOOL' in attribute:
            return str(attribute['BOOL'])
        
        return None
    
    def _transform_dynamodb_image_to_dict(self, image) -> Dict[str, Any]:
        """
        Transform DynamoDB image to flat dictionary
        
        Args:
            image: DynamoDB image object
            
        Returns:
            Dict[str, Any]: Flat dictionary with all attributes
        """
        result = {}
        
        # Convert image to dict if it's a Pydantic model
        if hasattr(image, 'model_dump'):
            image_dict = image.model_dump()
        else:
            image_dict = vars(image)
        
        for key, value in image_dict.items():
            if value is not None:
                extracted_value = self._extract_attribute_value(value)
                if extracted_value is not None:
                    # Try to convert numeric strings to numbers
                    if key in ['balance', 'amount'] and extracted_value.isdigit():
                        result[key] = int(extracted_value)
                    else:
                        result[key] = extracted_value
        
        return result