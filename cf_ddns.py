#!/usr/bin/python3
# pylint: disable=missing-module-docstring
# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=line-too-long
# pylint: disable=broad-exception-raised
# pylint: disable=broad-exception-caught

import sys
import json
import datetime
from time import sleep

import http.client

if __name__ == '__main__':

  # Read arguments
  if len(sys.argv) < 6:
    print('Usage: python cf_ddns.py <API_TOKEN> <DOMAIN> <RECORD_NAME> <TTL> <PROXIED> <SOURCE_IP (OPTIONAL)>')
    sys.exit(1)

  API_TOKEN = sys.argv[1]
  DOMAIN = sys.argv[2]
  RECORD_NAME = sys.argv[3]
  TTL = int(sys.argv[4])
  PROXIED = True if sys.argv[5] == 'true' else False
  SOURCE_IP = sys.argv[6] if len(sys.argv) == 7 else None

  API_BASE = 'api.cloudflare.com'

  def get_current_public_ip(source_ip=None) -> str:
    print()
    print('Getting current public IP, using source IP:',
          source_ip if source_ip is not None else 'None')

    if source_ip is not None:
      conn = http.client.HTTPConnection(
          'ifconfig.me', source_address=(source_ip, 0))
    else:
      conn = http.client.HTTPConnection('ifconfig.me')
    conn.request('GET', '/')
    response = conn.getresponse()
    data = response.read().decode()
    conn.close()
    if response.status == 200:
      print('Current public IP:', data)
      return data
    else:
      raise Exception('Failed to get public IP')

  def perform_http_request(api_token: str, method: str, endpoint: str, payload: dict = None) -> dict:

    # Set the request headers
    headers = {
        'Authorization': f'Bearer {api_token}',
        'Content-Type': 'application/json'
    }

    conn = http.client.HTTPSConnection(API_BASE)

    # Send a GET request
    if payload is None:
      conn.request(method, endpoint, headers=headers)
    else:
      conn.request(method, endpoint, headers=headers, body=json.dumps(payload))

    # Get the response
    response = conn.getresponse()

    status = response.status
    data = json.loads(response.read().decode())

    # Close the connection
    conn.close()

    # Print the response status code
    print('Response Status:', status)

    # Print the response body
    print('Response Body:', data)

    # Parsing JSON
    return status, data

  def verify_token(api_token: str) -> bool:
    print()
    print('Verifying API Token...')

    status, _ = perform_http_request(
        api_token, 'GET', '/client/v4/user/tokens/verify')

    if status == 200:
      print('Token is valid.')
      return True

    print('Token is invalid.')
    raise Exception('Token is invalid.')

  def get_zone_id(api_token: str, domain: str) -> str:
    # Print a blank line for readability
    print()

    # Print a message indicating that we are listing zones
    print('Listing Zones...')

    # Perform an HTTP request to get the list of zones
    status, data = perform_http_request(api_token, 'GET', '/client/v4/zones')

    if status != 200:
      # If the request was not successful, print an error message and raise an exception
      print('Failed to list zones.')
      raise Exception('Failed to list zones.')

    # Print a message indicating that we are getting the Zone ID of the specified domain
    print('Getting Zone ID of domain:', domain)

    # Iterate over the list of zones returned by the API
    for zone in data['result']:
      # Check if the name of the zone matches the specified domain
      if zone['name'] == domain:
        # If a match is found, retrieve the Zone ID and print it
        zone_id = zone['id']
        print(f'Zone ID of {domain}:', zone_id)
        return zone_id

    # If no match is found, print a message indicating that the Zone ID was not found
    print(f'Zone ID of {domain} not found')
    return None

  def get_record_id(api_token: str, record_name: str, domain: str, zone_id: str) -> str:
    # Print a blank line for readability
    print()

    # Print a message indicating that we are getting DNS records
    print('Getting DNS records...')

    # Perform an HTTP request to get the DNS records for the specified zone
    status, data = perform_http_request(
        api_token, 'GET', f'/client/v4/zones/{zone_id}/dns_records')

    # Check if the request was successful
    if status != 200:
      # If the request was not successful, print an error message and raise an exception
      print('Failed to get DNS records.')
      raise Exception('Failed to get DNS records')

    # Print a message indicating that we are finding the DNS record ID
    print(f'Finding DNS record ID of {record_name}.{domain}...')

    # Iterate over the DNS records returned by the API
    for record in data['result']:
      # Check if the name of the record matches the specified record name and domain
      if record['name'] == f'{record_name}.{domain}':
        # If a match is found, retrieve the record ID and print it
        record_id = record['id']
        print(f'DNS Record ID of {record_name}.{domain}:', record_id)
        return record_id

    # If no match is found, print a message indicating that the DNS record was not found
    print(f'DNS Record {record_name}.{domain} not found')
    return None

  def overwrite_record(api_token: str, record_type: str, record_name: str, domain: str, record_value: str, ttl: int, proxied: bool, zone_id: str, record_id: str) -> bool:
    # Print a blank line for readability
    print()
    # Print a message indicating that we are overwriting the DNS record
    print('Overwriting DNS record...')

    # Get the current timestamp
    timestamp = datetime.datetime.now().isoformat()

    # Create the payload for the API request
    payload = {
        'content': record_value,
        'name': f'{record_name}.{domain}',
        'proxied': proxied,
        'type': record_type,
        'comment': f'Updated by DDNS Client at {timestamp}.',
        'ttl': ttl
    }

    # Perform the HTTP request to update the DNS record
    status, _ = perform_http_request(
        api_token, 'PUT', f'/client/v4/zones/{zone_id}/dns_records/{record_id}', payload)

    # Check if the request was successful
    if status != 200:
      # If the request was not successful, print an error message and raise an exception
      print('Failed to update DNS record.')
      raise Exception('Failed to update DNS record')

    # Print a message indicating that the DNS record was successfully updated
    print(f'{RECORD_NAME}.{DOMAIN} with type {RECORD_TYPE} updated to {RECORD_VALUE} where TTL is {TTL} and Proxied is {PROXIED}.')
    return True

  def add_record(api_token: str, record_type: str, record_name: str, domain: str, record_value: str, ttl: int, proxied: bool, zone_id: str) -> bool:
    # Print a blank line for readability
    print()
    # Print a message indicating that we are overwriting the DNS record
    print('Adding DNS record...')

    # Get the current timestamp
    timestamp = datetime.datetime.now().isoformat()

    # Create the payload for the API request
    payload = {
        'content': record_value,
        'name': f'{record_name}.{domain}',
        'proxied': proxied,
        'type': record_type,
        'comment': f'Created by DDNS Client at {timestamp}.',
        'ttl': ttl
    }

    # Perform the HTTP request to update the DNS record
    status, _ = perform_http_request(
        api_token, 'POST', f'/client/v4/zones/{zone_id}/dns_records', payload)

    # Check if the request was successful
    if status != 200:
      # If the request was not successful, print an error message and raise an exception
      print('Failed to create DNS record.')
      raise Exception('Failed to create DNS record')

    # Print a message indicating that the DNS record was successfully updated
    print(f'{record_name}.{domain} with type {record_type} created to {record_value} where TTL is {ttl} and Proxied is {proxied}.')
    return True

  def perform_ddns(api_token: str, domain: str, record_type: str, record_name: str, record_value: str, ttl: int, proxied: bool) -> bool:
    # Verify the token
    verify_token(api_token)

    # Get the zone ID
    zone_id = get_zone_id(api_token, domain)

    # Get the record ID
    record_id = get_record_id(api_token, record_name, domain, zone_id)

    # If record ID is not found, add a new record
    if record_id is None:
      return add_record(api_token, record_type, record_name, domain, record_value, ttl, proxied, zone_id)

    # Overwrite the existing record
    return overwrite_record(api_token, record_type, record_name, domain, record_value, ttl, proxied, zone_id, record_id)

  MAX_RETRY = 3

  while MAX_RETRY > 0:
    try:
      if SOURCE_IP is not None:
        RECORD_VALUE = get_current_public_ip(SOURCE_IP)
      else:
        RECORD_VALUE = get_current_public_ip()

      # Check IP version
      if '.' in RECORD_VALUE:
        RECORD_TYPE = 'A'
      elif ':' in RECORD_VALUE:
        RECORD_TYPE = 'AAAA'

      perform_ddns(API_TOKEN, DOMAIN, RECORD_TYPE,
                   RECORD_NAME, RECORD_VALUE, TTL, PROXIED)
      break
    except Exception as e:
      print('An error occurred:', e)
      MAX_RETRY -= 1
      sleep(5)
      continue

  if MAX_RETRY == 0:
    print('Failed to update DNS record after 3 retries.')
    sys.exit(1)
