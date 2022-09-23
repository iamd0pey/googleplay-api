#!/usr/bin/env python3

from gpapi.googleplay import GooglePlayAPI, config

import os

import click
import download
import accounts

LOCALE = os.environ["GPAPI_LOCALE"]
TIMEZONE = os.environ["GPAPI_TIMEZONE"]

@click.group()
@click.option('--debug/--no-debug', default=False)
def cli(debug):
    click.echo(f"Debug mode is {'on' if debug else 'off'}")

@cli.command(help = "Add a new google account")  # @cli, not @click!
@click.option("--email", required=True, help="The email for your device Google account")
@click.option("--password", required=True, help="The password for your Google account or an App password")
@click.option("--device", default=None, help="The device code name, e.g angler. [default: random]")
@click.option("--locale", default=LOCALE, show_default=True, help="The locale for your Google account, e.g en_PT.")
@click.option("--timezone", default=TIMEZONE, show_default=True, help="The timezone for your Google account, e.g Europe/Lisbon.")
def account(email, password, device, locale, timezone):
    click.echo('Creating a new account...')
    click.echo(f"email: {email}")
    click.echo(f"password: {password}")
    click.echo(f"device: {device}")

    account = {
        'email': email,
        'password': password,
        'device_code_name': device,
        'locale': locale,
        'timezone': timezone,
        'gsfid': None,
        'authSubToken': None,
    }

    accounts.random_login_for_device(device)
    exit()

    if not accounts.save(account):
        click.secho(f"Unable to add account due to failure in the Login", err=True, fg='red')
        exit(1)

    click.secho(f"Account created...", fg='green')


@cli.command(help="List all device hardware identifiers")
def devices():
    click.echo(config.getDevicesCodenames())


if __name__ == '__main__':
    cli(obj={})
