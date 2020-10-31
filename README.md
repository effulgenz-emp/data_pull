# Cassandra database to parquet files

## How to run?

### Prerequisites:

1. Install Python.
   * Download & Install latest version of python from [here](https://www.python.org/downloads/)
2. Update the cassandra_config.ini file.

   ```
    IP_ADDRESS = <<IP>>
    PORT = <<Port>>
    USER = <<User>>
    PWD = <<Password>>
    KEY_SPACE = <<KeySpace>>
    ```

   1. Encode your password using password_encode.py
   2. Open command prompt and go to the project directory
   3. Run *python password_encoder.py*
        ```python
        Enter the password to encode: password1234
        Your encoded password - b'cGFzc3dvcmQxMjM0'
   4. Copy the encoded password and add it in cassandra_config.ini

    Example: *(Strings without quote)*
    ```
    IP_ADDRESS = 255.255.0.0
    PORT = 9042
    USER = username
    PWD = cGFzc3dvcmQxMjM0
    KEY_SPACE = keyspace
    ```

3. Install required libraries from requirements.txt file.
    * Open command prompt and go to project directory.
    * Execute the following command

    ```
    pip install -r requirements.txt
    ```

4. Run the cassandra_data_pull.py file.
    ```
    python cassandra_data_pull.py
    ```

## Output

1. Script will create data and log folder in the project directory.
    * data - all parquet files
    * log - log files
        * last 10 log files only available (configurable in logging.conf file)
