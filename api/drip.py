import json
import requests
import os
import concurrent.futures
try:
    from api.batch_post import BatchPost
    from api.constituent import Constituent
except ModuleNotFoundError:
    from batch_post import BatchPost
    from constituent import Constituent


def drip(batch: BatchPost, test=False):
    tag = batch.tag
    tag_status = batch.tag_state

    drip_token = os.environ['DRIP_TOKEN']
    account_ID = os.environ['DRIP_ACCOUNT'] # if not test else os.environ['DRIP_TEST_ACCOUNT']

    authorization = f'Bearer {drip_token}'
    headers = {"Authorization": authorization}

    def tag_email(constit: Constituent):
        if constit.do_not_email:
            print('no consent')
            constit.status('no consent')
            return

        url = f'https://api.getdrip.com/v2/{account_ID}/tags'
        payload= {
            "tags": [{ 
                "email": 'lokijybap@mailinator.com', 
                "tag": tag
            }]
        }
        data = json.dumps(payload)
        response = requests.post(url, headers=headers, data=data, timeout=8)
        outcome = 'successly tagged.' if response.status_code == 201 else 'tagging failed.'
        # print(f'{email} {success}')
        if outcome == 'tagging failed.':
            constit.status('tag failed')
            print(response.content)
        else:
            constit.status('success')


    def untag_email(constit: Constituent):
        url = f"https://api.getdrip.com/v2/{account_ID}/subscribers/{constit.email}/tags/{tag}"

        response = requests.delete(url, headers=headers)
        outcome = 'successfully untagged.' if response.status_code == 204 else 'untagging failed.'
        if outcome == 'tagging failed.':
            constit.status('tag failed')
        else:
            constit.status('success')

    drip_function = tag_email if tag_status else untag_email

    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(drip_function, constit) for constit in batch.constits]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
