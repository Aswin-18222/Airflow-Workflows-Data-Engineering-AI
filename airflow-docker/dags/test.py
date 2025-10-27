import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '../scripts'))

from News_ingestion_Kafka import main as producer_main

producer_main()