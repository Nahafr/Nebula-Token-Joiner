"""Startup Files which stores A HandleSetup Class."""

from typing import Optional, Tuple, Union

import time
import sys
import os

from bs4 import BeautifulSoup

import requests

from helper import Utils, NebulaLogging, NebulaColor, config


class HandleSetup:
    """A class responsible for handling various setup tasks for the Token Joiner tool."""

    @staticmethod
    def fetch_user_agent() -> str:
        """Fetch the latest user agent from our website."""
        try:
            auratoolsxyz = "https://headers.auratools.xyz/"  # old website
            response = requests.get(auratoolsxyz, timeout=5)
            soup = BeautifulSoup(response.text, "html.parser")
            body = soup.body
            if body is None:
                return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            user_agent = body.get_text(strip=True)
            if not user_agent:
                return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            return user_agent
        except (requests.RequestException, AttributeError):
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

    @staticmethod
    def show_initial_title():
        """Display the initial title with an option to skip the animation."""
        Utils.new_title(
            "Token Joiner discord.gg/nebulatools ┃ Press S to skip animation"
        )

    @staticmethod
    def setup_headers(discord, user_agent: str, xcontext: tuple = None):
        """Set up headers for the Discord instance."""
        print(
            f"{NebulaLogging.LC} {NebulaColor.LIGHTBLACK}Building Headers...{NebulaColor.RESET}"
        )
        discord.fill_headers(token="", user_agent=user_agent, xcontext=xcontext)
        print(
            f"{NebulaLogging.LC} {NebulaColor.GREEN}Headers Built!{NebulaColor.RESET}"
        )

    @staticmethod
    def handle_proxies(
        utils_instance,
    ) -> Optional[str]:
        """Handle proxy usage based on user input."""
        if utils_instance.load("input/proxies.txt") != 0:
            if config["proxy"]["enabled"]:
                return config["proxy"]["mode"]

        return None

    @staticmethod
    def get_invite_link() -> str:
        """Get and sanitize the invite link from the user."""
        invite = input(
            f"{NebulaLogging.LC}{NebulaColor.LIGHTBLACK} Invite:{NebulaColor.Nebula} "
        ).strip()
        if ".gg/" in invite:
            return invite.split(".gg/")[1]
        if "invite/" in invite:
            return invite.split("invite/")[1]
        return invite

    @staticmethod
    def get_invite_links() -> list[str]:
        """Get invite links from file."""
        invite_file = input(
            f"{NebulaLogging.LC}{NebulaColor.LIGHTBLACK} Invite Links File (.txt):{NebulaColor.Nebula} "
        ).strip().replace('"', '')
        try: 
            with open(invite_file, "r", encoding="utf-8") as file:
                invites = [
                    invite.strip().split(".gg/")[1] if ".gg/" in invite else
                    invite.strip().split("invite/")[1] if "invite/" in invite else
                    invite.strip()
                    for invite in file.readlines()
                ]
                if not invites:
                    print(f"{NebulaLogging.LC}{NebulaColor.RED} Invites Failed to loas or file is empty!{NebulaColor.Nebula}")
                    sys.exit(1)
                print(f"{NebulaLogging.LC}{NebulaColor.GREEN} Successfully loaded invites list!{NebulaColor.Nebula}")
                return invites
        except FileNotFoundError:
            ValueError("File does not exist!")


    @staticmethod
    def validate_invite(invite: str):
        """Validate the Discord invite link."""
        url = f"https://discord.com/api/v9/invites/{invite}"
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(
                    f"{NebulaLogging.LC} {NebulaColor.LIGHTBLACK}Invite -> {NebulaColor.GREEN}Valid{NebulaColor.RESET}"
                )
            elif response.status_code == 429:
                print(
                    f"{NebulaLogging.LC} {NebulaColor.RED}Rate Limited. Continuing without checking.{NebulaColor.RESET}"
                )
            else:
                print(
                    f"{NebulaLogging.LC} {NebulaColor.LIGHTBLACK}Invite -> {NebulaColor.RED}Invalid{NebulaColor.RESET}"
                )
                time.sleep(2)
                sys.exit("Invalid invite. Exiting...")
        except requests.RequestException as e:
            print(
                f"{NebulaLogging.LC} {NebulaColor.RED}Failed to validate invite: {e}{NebulaColor.RESET}"
            )
            sys.exit("Error validating invite. Exiting...")

    @staticmethod
    def get_nickname() -> Optional[str]:
        """Prompt the user for a nickname."""
        if config["appearance"]["ask_in_ui"]:
            if (
                input(
                    f"{NebulaLogging.LC}{NebulaColor.LIGHTBLACK} Change Nick? (y/n):{NebulaColor.Nebula} "
                )
                .strip()
                .lower()
                == "y"
            ):
                nickname = input(
                    f"{NebulaLogging.LC}{NebulaColor.LIGHTBLACK} Nickname:{NebulaColor.Nebula} "
                ).strip()
                print(
                    f"{NebulaLogging.LC} {NebulaColor.LIGHTBLACK}Nickname -> {NebulaColor.GREEN}{nickname}{NebulaColor.RESET}"
                )
                return nickname
            return None
        
        if config["appearance"]["nickname_enabled"]:
            return config["appearance"]["nickname"]

    @staticmethod
    def get_delay() -> tuple[int, int] | tuple[None, None]:
        """Prompt the user for joining delay."""
        
        def delay_prompt(prompt: str) -> int:
            while True:
                try:
                    return int(input(prompt).strip())
                except ValueError:
                    print(f"{NebulaLogging.LC}{NebulaColor.RED} Invalid input. Please enter a valid integer.{NebulaColor.RESET}")

        if config["delay"]["ask_in_ui"]:
            confirm = input(
                f"{NebulaLogging.LC}{NebulaColor.LIGHTBLACK} Join Delay? (y/n):{NebulaColor.Nebula} "
            ).strip().lower()

            if confirm == "y":
                delay_min = delay_prompt(
                    f"{NebulaLogging.LC}{NebulaColor.LIGHTBLACK} Minimum Delay (in seconds):{NebulaColor.Nebula} "
                )
                print(
                    f"{NebulaLogging.LC}{NebulaColor.LIGHTBLACK} Minimum Delay set to -> {NebulaColor.GREEN}{delay_min}{NebulaColor.RESET}"
                )

                delay_max = delay_prompt(
                    f"{NebulaLogging.LC}{NebulaColor.LIGHTBLACK} Maximum Delay (in seconds):{NebulaColor.Nebula} "
                )
                print(
                    f"{NebulaLogging.LC}{NebulaColor.LIGHTBLACK} Maximum Delay set to -> {NebulaColor.GREEN}{delay_max}{NebulaColor.RESET}"
                )

                return delay_min, delay_max

            return None, None

        if config["delay"]["enabled"]:
            return config["delay"]["min"], config["delay"]["max"]

        return None, None


        

    @staticmethod
    def get_vcjoin() -> int:
        
        confirm = input(
            f"{NebulaLogging.LC}{NebulaColor.LIGHTBLACK} Join VC? (y/n):{NebulaColor.Nebula} "
        ).strip().lower()
        
        if confirm == "y":
                channel_id = input(
                    f"{NebulaLogging.LC}{NebulaColor.LIGHTBLACK} Channel ID:{NebulaColor.Nebula} "
                ).strip()
                
                try:
                    channel_id = int(channel_id)
                    print(
                        f"{NebulaLogging.LC}{NebulaColor.LIGHTBLACK} Joining VC -> {NebulaColor.GREEN}{channel_id}{NebulaColor.RESET}"
                    )
                    return channel_id
                except ValueError:
                    print(
                        f"{NebulaLogging.LC}{NebulaColor.RED} Invalid input. Please enter a valid channel id.{NebulaColor.RESET}"
                    )

    @staticmethod
    def get_image() -> str:
        """
        Prompt the user to input an image URL or file path, 
        then convert the image to a Base64 string.
        """
        while True:
            choice = input(
                f"{NebulaLogging.LC}{NebulaColor.LIGHTBLACK} Enter image source - URL (u) or Path (p): {NebulaColor.Nebula}"
            ).strip().lower()

            if choice == "u":
                image_url = input(
                    f"{NebulaLogging.LC}{NebulaColor.LIGHTBLACK} Enter Image URL: {NebulaColor.Nebula}"
                ).strip()
                
                if not image_url.startswith(("http://", "https://")):
                    print(
                        f"{NebulaLogging.LC}{NebulaColor.RED} Invalid URL. Please provide a valid URL.{NebulaColor.RESET}"
                    )
                    continue

                try:
                    path = Utils.download_image(url=image_url)
                    return Utils.image_to_base64(image_path=path)
                except Exception as e:
                    print(
                        f"{NebulaLogging.LC}{NebulaColor.RED} Error: {e}{NebulaColor.RESET}"
                    )

            elif choice == "p":
                image_path = input(
                    f"{NebulaLogging.LC}{NebulaColor.LIGHTBLACK} Enter Image Path (Drag & Drop): {NebulaColor.Nebula}"
                ).strip()

                if not os.path.isfile(image_path):
                    print(
                        f"{NebulaLogging.LC}{NebulaColor.RED} Invalid file path. Please provide a valid path.{NebulaColor.RESET}"
                    )
                    continue

                try:
                    return Utils.image_to_base64(image_path=image_path)
                except Exception as e:
                    print(
                        f"{NebulaLogging.LC}{NebulaColor.RED} Error: {e}{NebulaColor.RESET}"
                    )

            else:
                print(
                    f"{NebulaLogging.LC}{NebulaColor.RED} Invalid input. Please type 'u' for URL or 'p' for Path.{NebulaColor.RESET}"
                )
