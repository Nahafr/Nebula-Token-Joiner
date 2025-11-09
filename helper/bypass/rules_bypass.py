"""Python File for Bypassing Rules."""

from typing import Dict, Union

import curl_cffi.requests

from helper.Utils.logging import NebulaLogging
from helper.Utils.utils import Discord
from helper.NebulaColors.color import NebulaColor

class BypassRules:
    """Class for Onboarding Bypass."""

    def __init__(
        self, token: str, guild_id: int, useragent:str, proxy: str | None = None
    ) -> None:
        """Initializes the BypassRules class."""
        self.session = curl_cffi.requests.Session(impersonate="chrome")

        self.token: str = token
        self.guild_id: int = guild_id
        self.headers: Dict[str, str] = self.build_rules_headers(
            useragent=useragent,
            token=token
        )

        if proxy:
            self.session.proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
            }

        
    def build_rules_headers(self, useragent: str, token: str) -> Dict[str, str]:
        version = Discord.extract_version(useragent)
        return {
            "authority": "discord.com",
            "accept": "*/*",
            "accept-language": "en-US",
            "authorization": token,
            "content-type": "application/json",
            "origin": "https://discord.com",
            "priority": "u=1, i",
            "referer": "https://discord.com/channels/@me",
            "sec-ch-ua": f'"Google Chrome";v="{version}", "Chromium";v="{version}", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": useragent,
            "x-debug-options": "bugReporterEnabled",
            "x-discord-locale": "en-US",
            "x-discord-timezone": "Europe/Berlin",
            "x-super-properties": Discord.build_properties(user_agent=useragent)
        }
    def get_data(self) -> Union[tuple[str, list], None]:
        """Fetches rules data."""

        response = self.session.get(
            f"https://discord.com/api/v9/guilds/{self.guild_id}/member-verification?with_guild=false&invite_code=",
            headers=self.headers,
        )

        if response.status_code == 200:
            data = response.json()
            return data.get("version"), data.get(
                "form_fields"
            )

        NebulaLogging.print_error(
            token=self.token,
            message="Error",
            response=response
        )
        return None

    def bypass_rules(self) -> None:
        """Main function to bypass rules."""
        try:
            version, form_fields = self.get_data()

            response = self.session.put(
                f"https://discord.com/api/v9/guilds/{self.guild_id}/requests/@me",
                headers=self.headers,
                json={
                    "version": version,
                    "form_fields": form_fields,
                },
            )

            if response.status_code == 201:
                NebulaLogging.print_status(
                    token=self.token,
                    message="Bypassed Rules",
                    color=NebulaColor.GREEN
                )
            else:
                NebulaLogging.print_error(
                    token=self.token,
                    message="Error",
                    response=response
                )
                
        except Exception as e:
            NebulaLogging.print_status(self.token, f"Error While Trying to Bypass Rules: {str(e)}", NebulaColor.RED)