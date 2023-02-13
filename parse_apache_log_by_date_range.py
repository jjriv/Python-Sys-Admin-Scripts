import re
import sys
from datetime import datetime

def parse_log_file(filename, start_time, end_time):
    # Compile the regular expression pattern for extracting timestamps
    pattern = re.compile(r'\d{2}/\w{3}/\d{4}:\d{2}:\d{2}:\d{2}')
    
    with open(filename, 'r') as log_file:
        for line in log_file:
            # Extract the timestamp from the line
            match = pattern.search(line)
            if match:
                timestamp = datetime.strptime(match.group(0), '%d/%b/%Y:%H:%M:%S')
                
                # Check if the timestamp is within the specified range
                if start_time <= timestamp <= end_time:
                    print(line.strip())

if __name__ == '__main__':
    logfilename = sys.argv[1]
    start_time = datetime.strptime(sys.argv[2], '%Y-%m-%d %H:%M:%S')
    end_time = datetime.strptime(sys.argv[3], '%Y-%m-%d %H:%M:%S')
    parse_log_file(logfilename, start_time, end_time)
