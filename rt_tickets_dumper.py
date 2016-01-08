#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import re
import requests
import os


class RtDumper:
    attachments_regexp = re.compile('(?P<attachment_id>\d+):\s?(?P<filename>.+)\s\(')
    useragent = 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36'

    def __init__(self, dump_directory, rt_host, username, password, schema='http'):
        self.dump_directory = dump_directory
        self.rt_host = rt_host
        self.username = username
        self.password = password
        self.schema = schema
        self.referer = '{0}://{1}/'.format(self.schema, self.rt_host)
        self.headers = {
            'User-Agent': self.useragent,
            'Referer': self.referer
        }
        self.cookies_dict = self._get_session_cookies()

    def _get_session_cookies(self):
        session = requests.Session()
        rt_auth_url = '{0}://{1}/'.format(self.schema, self.rt_host)
        session.post(rt_auth_url, data='user={0}&pass={1}'.format(self.username, self.password))
        try:
            rt_cookies = session.cookies
        except:
            rt_cookies = None
        session.close()
        return rt_cookies

    def get_ticket_history(self, ticket_id):
        if self.cookies_dict:
            url = '{0}://{1}/REST/1.0/ticket/{2}/history?format=l'.format(self.schema, self.rt_host, ticket_id)
            req = requests.get(url, headers=self.headers, cookies=self.cookies_dict, verify=False)
            response = req.content
            if '# Ticket {0} does not exist.'.format(ticket_id) not in response:
                ticket_download_dir = os.path.join(self.dump_directory, str(ticket_id))
                if not os.path.isdir(ticket_download_dir):
                    os.makedirs(ticket_download_dir)
                with open(os.path.join(ticket_download_dir, 'ticket_history.txt'), 'w') as outfile:
                    outfile.write(response)
                return True
            else:
                return

    def download_attachment(self, ticket_id, attachment_id, attachment_filename):
        if self.cookies_dict:
            url = '{0}://{1}/REST/1.0/ticket/{2}/attachments/{3}/content'.format(self.schema,
                                                                                 self.rt_host,
                                                                                 ticket_id,
                                                                                 attachment_id
                                                                                 )
            req = requests.get(url, headers=self.headers, cookies=self.cookies_dict, verify=False)
            try:
                attachment = req.content.split('\n\n', 1)[1]
                ticket_download_dir = os.path.join(self.dump_directory, str(ticket_id))
                if not os.path.isdir(ticket_download_dir):
                    os.makedirs(ticket_download_dir)
                with open(os.path.join(ticket_download_dir, attachment_filename), 'wb') as outfile:
                    outfile.write(attachment)
            except IndexError:
                pass

    def get_ticket_attachments(self, ticket_id):
        if self.cookies_dict:
            url = '{0}://{1}/REST/1.0/ticket/{2}/attachments'.format(self.schema, self.rt_host, ticket_id)
            req = requests.get(url, headers=self.headers, cookies=self.cookies_dict, verify=False)
            response = req.text
            for line in response.splitlines():
                if self.attachments_regexp.search(line):
                    attachment_id, filename = self.attachments_regexp.search(line).groups()
                    if filename != '(Unnamed)':
                        self.download_attachment(ticket_id, attachment_id, filename)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Tool for Best Practical Request Tracker tickets dumping.')
    parser.add_argument(
            '-f',
            '--folder',
            help='Directory for tickets export (will be created if does not exist).',
            required=True
    )
    parser.add_argument(
            '-d',
            '--domain',
            help='Domain of Requests Tracker.',
            required=True
    )
    parser.add_argument(
            '-u',
            '--username',
            help='Your Requests Tracker account username.',
            required=True
    )
    parser.add_argument(
            '-p',
            '--password',
            help='Your Requests Tracker account password.',
            required=True
    )
    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        os.makedirs(args.folder)

    dumper = RtDumper(
            dump_directory=args.folder,
            rt_host=args.domain,
            username=args.username,
            password=args.password
    )
    current_ticket_id = 1
    all_data_processed = 0
    while True:
        ticket_exists = dumper.get_ticket_history(current_ticket_id)
        if ticket_exists:
            dumper.get_ticket_attachments(current_ticket_id)
            current_ticket_id += 1
        else:
            all_data_processed = 1
        if all_data_processed != 0:
            break
