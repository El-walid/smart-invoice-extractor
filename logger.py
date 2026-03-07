import logging
import sys

# 1. Configure the logger
# We want to see logs in the Docker terminal (StreamHandler)
# AND save them to a file (FileHandler) for history.

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout), # Print to terminal
        logging.FileHandler("invoice_extractor.log") # Save to file
    ]
)

# 2. Create a logger object we can import elsewhere
logger = logging.getLogger("smart-invoice-extractor")