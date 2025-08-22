from abc import ABC, abstractmethod
from typing import List, Optional
from domain.models.dynamodb_record import DynamoDBStreamRecord, ProcessedRecord


class RecordProcessorPort(ABC):
    """Port for processing DynamoDB Stream records"""
    
    @abstractmethod
    def parse_stream_record(self, record: dict) -> DynamoDBStreamRecord:
        """Parse raw DynamoDB Stream record"""
        pass
    
    @abstractmethod
    def transform_record(self, stream_record: DynamoDBStreamRecord) -> Optional[ProcessedRecord]:
        """Transform DynamoDB Stream record to ProcessedRecord"""
        pass
    
    @abstractmethod
    def should_process_record(self, processed_record: ProcessedRecord) -> bool:
        """Determine if record should be processed for notifications"""
        pass