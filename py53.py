import argparse

import boto3
import dns.resolver


def main():
    parser = argparse.ArgumentParser(description='Update an A record in AWS Route 53')
    parser.add_argument('--hosted_zone_id', required=True, help='The ID of the hosted zone')
    parser.add_argument('--domain_name', required=True, help='The domain name')
    parser.add_argument('--record_type', default='A', help='The record type (default: A)')
    parser.add_argument('--ttl', type=int, default=300, help='The time to live (TTL) (default: 300)')

    args = parser.parse_args()

    ip = get_public_ip()
    update_route53(args, ip)

    print(f"{args.domain_name} updated to {ip}")


def get_public_ip() -> str:
    resolver = dns.resolver.Resolver()
    resolver.nameservers = ["208.67.222.222"]  # resolver4.opendns.com
    query = resolver.resolve("myip.opendns.com", "A")
    for rdata in query:
        return rdata.to_text()


def update_route53(args, ip: str):
    session = boto3.Session(profile_name="py53")
    client = session.client('route53')

    client.change_resource_record_sets(
        HostedZoneId=args.hosted_zone_id,
        ChangeBatch={
            'Comment': 'update record',
            'Changes': [{
                'Action': 'UPSERT',
                'ResourceRecordSet': {
                    'Name': args.domain_name,
                    'Type': args.record_type,
                    'TTL': args.ttl,
                    'ResourceRecords': [{'Value': ip}]
                }
            }]
        }
    )


if __name__ == '__main__':
    main()
