# `iba.py`: Create IBA Analyzer `.dat` Files Without the IBA Library  
A lightweight, open-source tool to generate and parse **ibaAnalyzer-compatible `.dat` files**—no proprietary IBA software or libraries required.  


## Key Features  
- **No IBA Dependencies**: Works independently of the official IBA library.  
- **Bidirectional Conversion**: JSON ↔ `.dat` (create `.dat` from JSON, or extract data from existing `.dat` files).  
- **Simple API**: Use via CLI or directly in Python code.  
- **ibaAnalyzer Compatibility**: Generates `.dat` files that open seamlessly in ibaAnalyzer.  


## Installation  
Since this package is not yet published to PyPI, install it locally from the GitHub repo:  

```bash
# Clone the repo
git clone https://github.com/ZisIsNotZis/iba.py.git
cd iba.py

# Install with pip (supports Python 3.8+)
pip install .
```


## Usage  

### 1. Command-Line Interface (CLI)  
Convert between JSON and `.dat` files with a single command.  

#### Example 1: JSON → `.dat` (Create IBA `.dat` File)  
Define your data in a JSON file (see [JSON Format](#json-format) below), then run:  
```bash
python -m iba_py your_data.json
```  
This generates `your_data.dat` in the same directory.  


#### Example 2: `.dat` → JSON (Extract Data from Existing `.dat`)  
To reverse-engineer a `.dat` file into human-readable JSON:  
```bash
python -m iba_py your_existing.dat
```  
This generates `your_existing.json` with the raw data, timestamps, and interval.  


### 2. Programmatic Usage (Python Code)  
Import `enc` (encode to `.dat`) and `dec` (decode from `.dat`) directly in your scripts.  

#### Example: Create a `.dat` File Programmatically  
```python
from iba_py import enc, dec

# Step 1: Define your data (match the JSON format)
begin_datetime = "2024-05-20T14:30:00"  # ISO 8601 datetime (ibaAnalyzer-compatible)
interval = 0.1  # Time between data points (0.1 seconds = 100ms)
data = {
    "Channel_A": [10.2, 10.3, 10.5, 10.4],  # List of values for Channel A
    "Channel_B": [20.1, 20.0, 19.8, 19.9]   # List of values for Channel B
}

# Step 2: Encode to .dat file
enc("output.dat", begin_datetime, interval, data)

# Step 3 (Optional): Decode the .dat file back to verify
decoded_dt, decoded_interval, decoded_data = dec("output.dat")
print("Decoded Begin Time:", decoded_dt)
print("Decoded Interval:", decoded_interval)
print("Decoded Data:", decoded_data)
```


## JSON Format  
The JSON file is a **3-element list** that defines the `.dat` file structure:  
```json
[
  "BEGIN_DATETIME",  # ISO 8601 datetime string (e.g., "2024-05-20T10:00:00")
  INTERVAL_SECONDS,  # Float: time between data points (e.g., 0.5 for 500ms)
  {                  # Data dictionary: channel names → value lists
    "CHANNEL_NAME_1": [VALUE_1, VALUE_2, ...],
    "CHANNEL_NAME_2": [VALUE_1, VALUE_2, ...]
  }
]
```

### Requirements for Valid JSON:  
- **Begin Datetime**: Must be an ISO 8601 string (ibaAnalyzer uses this as the start timestamp).  
- **Interval**: Must be a positive float (seconds between consecutive data points).  
- **Data Dictionary**:  
  - Keys: Valid channel names (strings, no special characters preferred).  
  - Values: Lists of **numerical values** (floats/integers). All lists must have the same length (one value per timestamp).  


## Example JSON File  
Save this as `sample_data.json`:  
```json
[
  "2024-05-20T09:00:00",
  0.2,
  {
    "Temperature_C": [22.5, 22.6, 22.7, 22.6, 22.5],
    "Pressure_kPa": [101.3, 101.4, 101.3, 101.2, 101.3],
    "Flow_LPM": [5.0, 5.1, 5.0, 4.9, 5.0]
  }
]
```

Generate the `.dat` file with:  
```bash
python -m iba_py sample_data.json
```


## Why This Project?  
The official IBA library is often:  
- Proprietary or restricted.  
- Tied to specific hardware/OS.  
- Overly complex for simple `.dat` creation.  

`iba.py` provides a **free, open alternative** for generating valid `.dat` files using standard JSON and Python.


## Troubleshooting  
If your `.dat` file doesn’t open in ibaAnalyzer:  
1. **Check JSON Validity**: Use a JSON linter (e.g., [jsonlint.com](https://jsonlint.com/)) to ensure no syntax errors.  
2. **Verify Data Lengths**: All value lists in the JSON must have the same length.  
3. **Datetime Format**: Ensure the begin datetime is ISO 8601 (e.g., `YYYY-MM-DDTHH:MM:SS`).  
4. **Interval Type**: The interval must be a float (e.g., `0.1`, not `"0.1"`).  


## Contributing  
Contributions are welcome! To contribute:  
1. Fork the repo.  
2. Create a feature branch (`git checkout -b feature/your-feature`).  
3. Commit your changes (`git commit -m 'Add your feature'`).  
4. Push to the branch (`git push origin feature/your-feature`).  
5. Open a Pull Request.  
