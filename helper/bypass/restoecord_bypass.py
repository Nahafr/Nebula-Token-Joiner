"""python file which Contains a class To bypass Restorecord"""
from typing import Dict

from helper.Utils.logging import NebulaLogging
from helper.NebulaColors.color import NebulaColor
from helper.Utils.utils import config, Discord


class RestoreCordBypass:
    """Class for Restorecord Bypass"""
    def __init__(
        self,
        token: str,
        guild_id: int,
        client_id: int,
        useragent: str,
        cfsession,
        proxy: str,
    ):
        """Initializes the RestoreCordBypass class."""
        self.session = cfsession
        self.token: str = token
        self.guild_id: int = guild_id
        self.client_id: int = client_id
        self.useragent: str = useragent
        self.proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",
        }
        
    def build_oath_headers(self, useragent: str, token: str) -> Dict[str, str]:
        version = Discord.extract_version(useragent)
        return {
        'Accept': '*/*',
        'Accept-Language': 'en-US',
        'Authorization': token,
        'Content-Type': 'application/json',
        'Origin': 'https://discord.com',
        'Priority': 'u=1, i',
        'Referer': 'https://discord.com/channels/@me',
        'Sec-CH-UA': f'"Google Chrome";v="{version}", "Chromium";v="{version}", "Not_A Brand";v="24"',
        'Sec-CH-UA-Mobile': '?0',
        'Sec-CH-UA-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'User-Agent': useragent,
        'X-Debug-Options': 'bugReporterEnabled',
        'X-Discord-Locale': 'es-ES',
        'X-Discord-Timezone': 'Europe/Berlin',
        'X-Super-Properties': Discord.build_properties(user_agent=useragent)
    }


    def bypass(self) -> None:
        """Function To Bypass Restorecord"""
        response = self.session.post(
            "https://discord.com/api/v9/oauth2/authorize",
            params={
                "client_id": self.client_id,
                "response_type": "code",
                "redirect_uri": "https://restorecord.com/api/callback",
                "scope": "identify guilds.join",
                "state": self.guild_id,
            },
            json={"permissions": "0", "authorize": True},
            headers=self.build_oath_headers(
                useragent=self.useragent, 
                token=self.token
            ),
            proxies=self.proxies,
        )

        try:
            data = response.json()
            if "location" not in data:
                NebulaLogging.print_error(
                    token=self.token,
                    message="Missing 'location' in response data",
                    response=response,
                )
                return False

            answer = data["location"]
            captcha_encounters = 0

            for attempt in range(5):
                attempt_response = self.session.get(
                    answer,
                    allow_redirects=True,
                    proxies=self.proxies,
                )

                if attempt_response.status_code in [307, 200]:
                    NebulaLogging.print_status(
                        token=self.token,
                        message="Restorecord Bypassed",
                        color=NebulaColor.GREEN,
                    )
                    return True

                if (
                    attempt_response.status_code == 403
                    and "Please complete the captcha to continue"
                    in attempt_response.text
                ):
                    captcha_encounters += 1
                    if config.get("debug"):
                        NebulaLogging.print_status(
                            token=self.token,
                            message="Error encountered while attempting to detect Restorecord: Cloudflare",
                            color=NebulaColor.RED,
                        )
                    continue

                NebulaLogging.print_error(
                    token=self.token,
                    message=f"Unexpected status code {attempt_response.status_code} on attempt {attempt + 1}",
                    response=attempt_response,
                )
                return False

            if captcha_encounters == 5:
                NebulaLogging.print_status(
                    token=self.token,
                    message="Error encountered while attempting to detect Restorecord: Cloudflare",
                    color=NebulaColor.RED,
                )
                return False

        except Exception as e:
            NebulaLogging.print_status(
                token=self.token,
                message=f"Error: {e}",
                color=NebulaColor.RED,
            )
            return False
