from typing import Dict, List, Optional

from src.entities.AccountCredentials import AccountCredentials
from src.entities.AccountType import AccountType
from src.entities.Proxy import Proxy
from src.entities.Schedule import Schedule
from src.ManagableAccount.ManagableAccount import ManagableAccount
from src.ManagableAccount.TiktokManagableAccount import TiktokManagableAccount
from src.utils.Logger import logger

# Adapter function to convert JSON to an optional ManagableAccount object
def json_to_managable_account(data: Dict) -> Optional[ManagableAccount]:
    """
    Convert JSON data into a ManagableAccount object if possible.

    Parameters:
    - data (dict): JSON data representing a ManagableAccount

    Returns:
    - Optional[ManagableAccount]: An instance of the ManagableAccount if created successfully, or None if invalid data.
    """
    # Parse proxy details
    proxy_data = data.get("proxy", None)

    if proxy_data == None:
        proxy = None
    else:
        proxy = Proxy(
            user=proxy_data.get("user"),
            password=proxy_data.get("password"),
            host=proxy_data.get("host"),
            port=proxy_data.get("port"),
        )

    # Parse account credentials
    credentials_data = data.get("credentials", None)

    if credentials_data == None:
        credentials = credentials_data
    else:
        credentials = AccountCredentials(
            login=credentials_data.get("login"),
            password=credentials_data.get("password"),
        )

    # Parse account type
    account_type = AccountType[data.get("accountType", "UNSPECIFIED")]

    # Parse schedule
    schedule_data = data.get("schedule", None)
    schedule = None
    if schedule_data != None:
        try:
            every_days = schedule_data["every_days"]
            schedule_time = []
            for time_i in schedule_data["at_time"]:
                schedule_time.append(time_i)
            schedule = Schedule(every_days, schedule_time)
        except:
            logger.info("Error happened during parsing managable accounts config: scheduler is not parsed")

    # Create and return the correct ManagableAccount instance based on account type
    if account_type == AccountType.TIKTOK:
        return TiktokManagableAccount(
            name=data.get("name"),
            description=data.get("description"),
            url=data.get("url"),
            proxy=proxy,
            credentials=credentials,
            accountType=account_type,
            schedule=schedule
        )

    return None


# Function to convert a list of JSON objects to a list of ManagableAccount objects, or None if no valid accounts found
def json_to_managable_accounts_list(
    data_list: List[Dict],
) -> Optional[List[ManagableAccount]]:
    """
    Convert a list of JSON objects into a list of ManagableAccount objects.

    Parameters:
    - data_list (List[Dict]): List of JSON objects representing ManagableAccount instances.

    Returns:
    - Optional[List[ManagableAccount]]: List of ManagableAccount objects if any are created, or None if no valid accounts.
    """
    accounts = []
    for data in data_list:
        account = json_to_managable_account(data)
        if account:
            accounts.append(account)

    return accounts if accounts else None
