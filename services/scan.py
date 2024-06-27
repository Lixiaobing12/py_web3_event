import time
from utils.logging import logger
from utils.db import get_db_connection
from utils.web3 import getW3
from utils.contract import getContract
import os


def get_event_logs_Registration(from_block, to_block):
    db = get_db_connection()
    cursor = db.cursor()
    w3 = getW3()
    contract = getContract()
    filter = contract.events.Registration().create_filter(
        fromBlock=from_block, toBlock=to_block
    )
    events = filter.get_all_entries()

    sqls = []
    for event in events:
        user_addr = event["args"]["user"]
        parent_addr = event["args"]["referrer"]
        tx_id = str(event["transactionHash"].hex())
        timestamp = w3.eth.get_block(event["blockNumber"])["timestamp"]
        time_array = time.localtime(timestamp)
        bind_at = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        cursor.execute(
            "select count(*) from bind_parents where user_addr = %s", user_addr
        )
        count = cursor.fetchone()[0]
        if count == 0:
            sqls.append(
                "insert into bind_parents (user_addr,parent_addr,tx_id,bind_at) values ('%s','%s','%s','%s')"
                % (user_addr, parent_addr, tx_id, bind_at),
            )
    db.close()
    return sqls


def get_event_logs_Reinvest(from_block, to_block):
    w3 = getW3()
    contract = getContract()
    db = get_db_connection()
    cursor = db.cursor()
    filter = contract.events.Reinvest().create_filter(
        fromBlock=from_block, toBlock=to_block
    )
    sqls = []
    for event in filter.get_all_entries():
        user_addr = event["args"]["user"]
        referrer_addr = event["args"]["currentReferrer"]
        level = event["args"]["level"]
        tx_id = str(event["transactionHash"].hex())
        action = "reinvest"
        caller_addr = event["args"]["caller"]
        timestamp = w3.eth.get_block(event["blockNumber"])["timestamp"]
        time_array = time.localtime(timestamp)
        deposit_at = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        cursor.execute(
            "select count(*) from deposits where tx_id = %s and action = %s",
            (tx_id, action),
        )
        count = cursor.fetchone()[0]
        if count == 0:
            sqls.append(
                "insert into deposits (user_addr,referrer_addr,\
                               level,tx_id,deposit_at,caller_addr,action) values ('%s','%s',%s,'%s','%s','%s','%s')"
                % (
                    user_addr,
                    referrer_addr,
                    level,
                    tx_id,
                    deposit_at,
                    caller_addr,
                    action,
                )
            )

    db.close()
    return sqls


def get_event_logs_Upgrade(from_block, to_block):
    w3 = getW3()
    db = get_db_connection()
    cursor = db.cursor()
    contract = getContract()
    filter = contract.events.Upgrade().create_filter(
        fromBlock=from_block, toBlock=to_block
    )
    sqls = []
    for event in filter.get_all_entries():
        user_addr = event["args"]["user"]
        referrer_addr = event["args"]["referrer"]
        level = event["args"]["level"]
        tx_id = str(event["transactionHash"].hex())
        timestamp = w3.eth.get_block(event["blockNumber"])["timestamp"]
        time_array = time.localtime(timestamp)
        deposit_at = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        action = "upgrade"
        caller_addr = event["args"]["user"]

        cursor.execute(
            "select count(*) from deposits where tx_id = %s and action = %s",
            (tx_id, action),
        )
        count = cursor.fetchone()[0]
        if count == 0:
            sqls.append(
                "insert into deposits (user_addr,referrer_addr,\
                               level,tx_id,deposit_at,caller_addr,action) values ('%s','%s',%s,'%s','%s','%s','%s')"
                % (
                    user_addr,
                    referrer_addr,
                    level,
                    tx_id,
                    deposit_at,
                    caller_addr,
                    action,
                )
            )
    db.close()
    return sqls


def get_event_logs_SentExtraRewardDividends(from_block, to_block):
    w3 = getW3()
    db = get_db_connection()
    cursor = db.cursor()
    contract = getContract()
    filter = contract.events.SentExtraRewardDividends().create_filter(
        fromBlock=from_block, toBlock=to_block
    )
    sqls = []
    for event in filter.get_all_entries():
        user_addr = event["args"]["from"]
        amount = event["args"]["amount"] / 10**18
        symbol = event["args"]["tokenAddress"] == os.getenv("USDT") and "USDT" or "KAI"
        tx_id = str(event["transactionHash"].hex())
        level = event["args"]["level"]
        timestamp = w3.eth.get_block(event["blockNumber"])["timestamp"]
        time_array = time.localtime(timestamp)
        reward_at = time.strftime("%Y-%m-%d %H:%M:%S", time_array)
        cursor.execute(
            "select count(*) from rewards where user_addr = %s and tx_id = %s",
            (user_addr, tx_id),
        )
        count = cursor.fetchone()[0]
        if count == 0:
            sqls.append(
                "insert into rewards (user_addr,amount,symbol,tx_id,level,reward_at) values ('%s',%s,'%s','%s',%s,'%s')"
                % (user_addr, amount, symbol, tx_id, level, reward_at)
            )

    db.close()
    return sqls


def start():
    w3 = getW3()
    db = get_db_connection()
    cursor = db.cursor()
    cursor.execute("select current_block_number, last_block_number from base_info")
    current_block, last_block = cursor.fetchone()
    # 获取最新区块
    latest_block = w3.eth.get_block("latest")["number"]
    if latest_block - last_block <= 1:
        db.close()
        print("No new block found, skip this mission")
        return
    try:
        while True:
            print(
                f"start scanning block number:{last_block}-{last_block + 10}",
            )
            regis_sqls, reinvest_sqls, upgrade_sqls, rewards_sqls = [], [], [], []
            try:
                regis_sqls = get_event_logs_Registration(last_block, last_block + 10)
                reinvest_sqls = get_event_logs_Reinvest(last_block, last_block + 10)
                upgrade_sqls = get_event_logs_Upgrade(last_block, last_block + 10)
                rewards_sqls = get_event_logs_SentExtraRewardDividends(
                    last_block, last_block + 10
                )
            except Exception as e:
                logger.error(
                    f"Error occurred while scanning block {last_block}-{last_block + 10}: {e}"
                )
                raise e
            for sql in regis_sqls + reinvest_sqls + upgrade_sqls + rewards_sqls:
                try:
                    cursor.execute(sql)
                except Exception as e:
                    logger.error(
                        f"Error occurred while executing sql: {sql}, error: {e}"
                    )
                    db.rollback()
                    raise e
            db.commit()
            if last_block + 10 > latest_block:
                break
            else:
                last_block += 10
    except Exception as e:
        db.close()
        print(e)

    else:
        cursor.execute("update base_info set last_block_number = %s", latest_block)
        db.commit()
        db.close()


def init():
    print("===> Scan service is running...")
    while True:
        start()
        time.sleep(60)
