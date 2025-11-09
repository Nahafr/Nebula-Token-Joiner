"""Python File for Bypassing Onboarding."""

from typing import Dict, Tuple, Union
import time
import random

import curl_cffi.requests

from helper.Utils.logging import NebulaLogging
from helper.Utils.utils import Discord
from helper.NebulaColors.color import NebulaColor

class OnboardingBypass:
    """Class for Onboarding Bypass."""

    def __init__(self, token: str, guildid: int, useragent: str, proxy: str | None = None) -> None:
        """Initializes the OnboardingBypass class."""
        self.session = curl_cffi.requests.Session(impersonate="chrome")
        self.token: str = token
        self.guildid: int = guildid
        self.headers: Dict[str, str] = self.build_onboarding_headers(
            useragent=useragent,
            token=token
        )
        
        if proxy:
            self.session.proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
            }
        
    def build_onboarding_headers(self, useragent: str, token: str) -> Dict[str, str]:
        version = Discord.extract_version(useragent)
        return {
            "authority": "discord.com",
            "accept": "*/*",
            "accept-language": "en-US",
            "authorization": token,
            "origin": "https://discord.com",
            "priority": "u=1, i",
            "referer": f"https://discord.com/channels{self.guildid}/@home",
            "sec-ch-ua": f'"Google Chrome";v="{version}", "Chromium";v="{version}", "Not_A Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-debug-options": "bugReporterEnabled",
            "x-discord-locale": "en-US",
            "x-discord-timezone": "Europe/Berlin",
            "x-super-properties": Discord.build_properties(user_agent=useragent)
        }   

    def fetch_onboarding_data(
        self,
    ) -> Union[Dict[str, Tuple[str, int, bool]], None]:
        """Fetches onboarding data."""
        response = self.session.get(
            f"https://discord.com/api/v9/guilds/{self.guildid}/onboarding",
            headers=self.headers,

        )

        if response.status_code == 200:
            return response.json()

        NebulaLogging.print_error(
            token=self.token,
            message="Error",
            response=response
        )
        return None

    def bypass_onboarding(self) -> None:
        """Main function to bypass onboarding."""
        try: 
            onboarding_data = self.fetch_onboarding_data()
            if not onboarding_data:
                return

            prompts = onboarding_data.get("prompts", [])
            responses = []
            prompts_seen = {}
            responses_seen = {}
            current_time = int(time.time() * 1000)

            for prompt in prompts:
                prompt_id = prompt.get("id")
                prompts_seen[prompt_id] = current_time

                options = prompt.get("options", [])
                for option in options:
                    option_id = option.get("id")
                    responses_seen[option_id] = current_time

                if prompt.get("single_select"):
                    if prompt.get("required", False) or random.choice([True, False]):
                        selected_option = random.choice(options) if options else None
                        if selected_option:
                            responses.append(selected_option["id"])
                else:
                    if not prompt.get("required", False):
                        selected_options = random.sample(
                            options,
                            k=random.randint(0, len(options))
                        )
                        for option in selected_options:
                            responses.append(option["id"])
                    else:
                        for option in options:
                            responses.append(option["id"])

            if not responses:
                print("No valid responses constructed for onboarding.")
                return

            response = self.session.post(
                f"https://discord.com/api/v9/guilds/{self.guildid}/onboarding-responses",
                json={
                "onboarding_responses": responses,
                "onboarding_prompts_seen": prompts_seen,
                "onboarding_responses_seen": responses_seen,
            },
                headers=self.headers,
            )

            if response.status_code == 200:
                NebulaLogging.print_status(
                    token=self.token,
                    message="Onboarding Bypassed",
                    color=NebulaColor.GREEN
                )
            else:
                error_message = response.json()
                NebulaLogging.print_error(
                    token=self.token,
                    message=f"Error: {error_message}",
                    response=response
                )

        except Exception as e:
            NebulaLogging.print_status(self.token, f"Error While Trying to Bypass Onboarding: {str(e)}", NebulaColor.RED)
            