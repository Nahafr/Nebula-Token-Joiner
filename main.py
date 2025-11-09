"Main File to handle Joining and more."

import ctypes
import threading
import time
import random 
from typing import Optional

import curl_cffi.requests
import cloudscraper

from helper import (
    Discord,
    Hsolver,
    Utils,
    config,
    fetch_session,
    intro,
    red_gradient,
    NebulaLogging,
    DetectBypass,
    OnboardingBypass,
    BypassRules,
    RestoreCordBypass,
    NebulaColor,
    HandleSetup,
    get_session_id,
    keep_session_alive
)

class NebulaStats:
    """Used to store stats for joining like: joined, failed, solved, .."""
    joined: list[str] = []
    failed: int = 0
    solved: int = 0
    start = None
    thread_running = threading.Event()
    
def title():
    """Function to show NebulaStats on title."""
    while not NebulaStats.thread_running.is_set():
        title = f"Nebula Token Joiner ┃ Joined: {len(NebulaStats.joined)} ┃ Failed: {NebulaStats.failed} ┃ Solved: {NebulaStats.solved} ┃ Time: {round(time.time() - NebulaStats.start, 2)}s "
        ctypes.windll.kernel32.SetConsoleTitleW(title)
        time.sleep(0.01) 
        
class NebulaTokenJoiner:
    """Handles Discord token joining and nickname changing."""

    def __init__(
        self, nickname: str, _proxy: bool, useragent: str, filling: bool = False
    ) -> None:
        """
        Initializes the NebulaTokenJoiner instance.

        Args:
            nickname (str): The nickname to set for the user.
            _proxy (bool): Whether to use proxies for requests.
            useragent (str): The User-Agent string for HTTP headers.
        """
        self.discord: callable = Discord()
        self.hsolver: callable = Hsolver()
        self.utils: callable = Utils()
        
        self.filling: bool = filling
        self.solver: bool = True
        self._proxy: bool = _proxy

        self.nickname: str = nickname
        self.useragent: str = useragent
        
        self.onboarding = None
        self.rules = None
        self.restorecord_detected = False
        self.client_id = None
        
        self.guild_id = None
        self.session_id: str = None

        self.lock = threading.Lock()

    def change_nick(
        self, guild_id: int, nick: str, token: str
    ) -> None:
        """
        Changes the nickname of a user in a specified Discord guild.

        Args:
            guild_id (int): The ID of the guild where the nickname is to be changed.
            nick (str): The new nickname to set.
            token (str): The Discord token for authentication.
        """
        headers = self.discord.fill_headers(
            token, self.useragent
        )
        session = curl_cffi.requests.Session(impersonate="chrome")
        session.headers.update(headers)
        session.cookies.update(
            self.discord.get_cookies(session)
        )
        if "{random}" in nick:
            random_number = random.randint(1111, 9999)
            nick = nick.replace("{random}", str(random_number))

        response = session.patch(
            f"https://discord.com/api/v9/guilds/{guild_id}/members/@me",
            json={"nick": nick},
            timeout=10
        )


        if response.status_code == 200:
            NebulaLogging.print_status(
                token, "Nickname Changed", NebulaColor.GREEN
            )
        elif response.status_code == 429:
            NebulaLogging.print_status(
                token, "Ratelimit", NebulaColor.RED
            )
        else:
            NebulaLogging.print_error(
                token,
                "Error while changing Nickname",
                response,
            )

    def accept_invite(
        self, invite: str, token: str, proxy: str = None, session_id: str = None
    ) -> None:
        """
        Accepts a Discord server invite and optionally changes the user's nickname.

        Args:
            invite (str): The server invite code.
            token (str): The Discord token for authentication.
            proxy (str, optional): Proxy to use for the request. Defaults to None.
        """
        session = curl_cffi.requests.Session(impersonate="chrome")
        try:
            if not session_id:
                session_id = fetch_session(token)
                if session_id == "Invalid token":
                    NebulaLogging.print_status(
                        token, "Invalid", NebulaColor.RED
                    )
                    return

                if session_id == "429":
                    NebulaLogging.print_status(
                        token,
                        "Cant Fetch Session -> 429",
                        NebulaColor.RED,
                    )
                    return

            self.session_id = session_id
            payload = {"session_id": self.session_id}
            session.cookies.update(
                self.discord.get_cookies(session)
            )

            if self._proxy:
                session.proxies = {
                "http": f"http://{proxy}",
                "https": f"http://{proxy}"
                }

            response = session.post(
                f"https://discord.com/api/v9/invites/{invite}",
                json=payload,
                headers=self.discord.fill_headers(
                    token, self.useragent
                ),
                timeout=config["join"]["timeout"]
            )

            if response.status_code == 200:
                self._handle_successful_invite(
                    token, response, self.nickname, proxy, invite
                )
                return
            
            elif response.status_code == 429:
                NebulaLogging.print_status(
                    token, "Ratelimit", NebulaColor.RED
                )
                with self.lock:
                    NebulaStats.failed += 1
            elif (
                response.status_code == 401
                and response.json()["message"]
                == "401: Unauthorized"
            ):
                NebulaLogging.print_status(
                    token, "Invalid", NebulaColor.RED
                )
                with self.lock:
                    NebulaStats.failed += 1
            elif (
                "You need to verify your account"
                in response.text
            ):
                NebulaLogging.print_status(
                    token, "Locked", NebulaColor.RED
                )
                with self.lock:
                    NebulaStats.failed += 1
            elif "captcha_rqdata" in response.text:
                self._handle_captcha(
                    token,
                    response,
                    invite,
                    session,
                    proxy,
                )
            else:
                NebulaLogging.print_error(
                    token, "Error while joining", response
                )
                
        except TimeoutError:
            NebulaLogging.print_status(token, "Timeout", NebulaColor.RED)
            with self.lock:
                NebulaStats.failed += 1
        except KeyError as e:
            NebulaLogging.print_status(token, f"Key Error: {e}", NebulaColor.RED)
            with self.lock:
                NebulaStats.failed += 1
        except Exception as e:
            error_message = str(e)
            if "curl: (28) Connection timed out" not in error_message:
                NebulaLogging.print_status(token, f"Error While Trying to join: {error_message}", NebulaColor.RED)
                with self.lock:
                    NebulaStats.failed += 1

    def _handle_successful_invite(
        self, token, response, nickname, proxy, invite = None
    ):
        """
        Handles the logic for a successful server join.

        Args:
            token (str): The Discord token used for the request.
            response (requests.Response): The response object from the server.
            nickname (str): The nickname to set, if any.
        """
        with self.lock:
            NebulaStats.joined.append(token)
            
        if self.filling and invite:
            NebulaLogging.print_status(
                token, f"Joined {NebulaColor.LIGHTBLACK}- ({invite})", NebulaColor.GREEN
            )
        
        else:
            NebulaLogging.print_status(
                token, "Joined", NebulaColor.GREEN
            )
            
        
        self.guild_id = response.json()["guild"]["id"]

        cfsess = cloudscraper.create_scraper(
            browser={
                "browser": "chrome",
                "platform": "windows",
                "desktop": True,
                "mobile": False,
            }
        )
        bypasses = config["join"]
        detect = DetectBypass(token=token, guildid=self.guild_id, useragent=self.useragent , proxy=proxy, cfsession=cfsess)
            
        self.onboarding = self.onboarding if self.onboarding is not None else detect.check_onboarding()
        self.rules = self.rules if self.rules is not None else detect.check_rules()
        
        if self.rules and bypasses["bypass_rules"]:
            NebulaLogging.print_status(
                token=token,
                message="Detected Rules",
                color=NebulaColor.LIGHTBLUE,
            )
            BypassRules(
                token=token, guild_id=self.guild_id, useragent=self.useragent, proxy=proxy
            ).bypass_rules()
            
        if self.onboarding and bypasses["bypass_onboarding"]:
            NebulaLogging.print_status(
                token=token,
                message="Detected Onboarding",
                color=NebulaColor.LIGHTBLUE,
            )
            OnboardingBypass(
                token=token, guildid=self.guild_id, useragent=self.useragent, proxy=proxy
            ).bypass_onboarding()
        
        if proxy and bypasses["bypass_restorecord"]:
            if not self.restorecord_detected:
                client_id = detect.check_restorecord()
                if client_id:
                    self.restorecord_detected = True
                    self.client_id = client_id
                else:
                    self.restorecord_detected = True  

            if self.client_id:
                NebulaLogging.print_status(
                    token=token,
                    message="Detected Restorecord",
                    color=NebulaColor.LIGHTBLUE,
                )
                RestoreCordBypass(
                    token=token,
                    guild_id=self.guild_id,
                    client_id=self.client_id,
                    useragent=self.useragent,
                    proxy=proxy,
                    cfsession=cfsess
                ).bypass()
                
        if nickname:
            self.change_nick(
                guild_id=self.guild_id,
                nick=nickname,
                token=token
            )

                    
            

    def _handle_captcha(
        self, token, response, invite, session, proxy_
    ):
        """
        Handles captcha challenges during the server joining process.

        Args:
            token (str): The Discord token used for the request.
            response (requests.Response): The response object from the server.
            invite (str): The server invite code.
            session (tls_client.Session): The current TLS session.
            proxy_ (str): Proxy used for the request.
        """
        NebulaLogging.print_status(
            token=token,
            message="Hcaptcha",
            color=NebulaColor.RED
        )
        if (
            config["captcha"]["api_key"]
            != "YOUR-24CAP-KEY | 24captcha.online" 
            and
            config["captcha"]["enabled"]
            and
            proxy_
        ):
            self._solve_captcha(
                token,
                response,
                invite,
                session,
                proxy_,
            )
        else:
            with self.lock:
                NebulaStats.failed += 1

    def _solve_captcha(
        self, token, response, invite, session, proxy_
    ):
        """
        Attempts to solve a captcha challenge using an external service.

        Args:
            token (str): The Discord token used for the request.
            response (requests.Response): The response object from the server.
            invite (str): The server invite code.
            session (tls_client.Session): The current TLS session.
            proxy_ (str): Proxy used for the request.
        """
        if self.solver:
            NebulaLogging.print_status(
                token=token[:45],
                message="Solving Captcha..",
                color=NebulaColor.GREEN
            )
            site_key = response.json()["captcha_sitekey"]
            rqdata = response.json()["captcha_rqdata"]
            rqtoken = response.json()["captcha_rqtoken"]

            try:
                start_time = time.time()
                status, solution = self.hsolver.get_captcha_key(
                    rqdata=rqdata,
                    site_key=site_key,
                    website_url="https://discord.com/channels/@me",
                    proxy=proxy_,
                    api_key=config["captcha"]["api_key"],
                )
                if status:
                    end_time = time.time()
                    NebulaStats.solved += 1
                    NebulaLogging.print_status(
                        token=solution,
                        message=f"{NebulaColor.GREEN}Solved in {NebulaColor.RESET}{end_time - start_time:.2f}s",
                        color=NebulaColor.GREEN,
                        length=60
                    )
                    headers = self.discord.fill_headers(
                        token=token, 
                        user_agent=self.useragent,
                        xcaptcha=solution,
                        rqtoken=rqtoken
                    )
                   
                    response = session.post(
                        f"https://discord.com/api/v9/invites/{invite}",
                        json={
                            "session_id": self.session_id
                        },
                        headers=headers,
                        timeout=config["join"]["timeout"]
                    )
                    

                    if response.status_code == 200:
                        with self.lock:
                            NebulaStats.joined.append(token)
                        
                        if not self.filling:
                            NebulaLogging.print_status(
                                token,
                                "Joined",
                                NebulaColor.GREEN,
                            )
                        else:
                            NebulaLogging.print_status(
                                token,
                                f"Joined {NebulaColor.LIGHTBLACK}- ({invite})",
                                NebulaColor.GREEN,
                            )
                        if self.nickname:
                            guild_id = response.json()[
                                "guild"
                            ]["id"]
                            self.change_nick(
                                guild_id,
                                self.nickname,
                                token,
                            )
                    else:
                        NebulaLogging.print_error(
                            token,
                            "Error while joining",
                            response,
                        )
                        with self.lock:
                            NebulaStats.failed += 1
                else:
                    NebulaLogging.print_status(
                        "Failed To Solve Captcha.",
                        solution,
                        NebulaColor.RED
                    )
                    with self.lock:
                        NebulaStats.failed += 1
                    return
            except (
                ConnectionError,
                TimeoutError,
            ) as conn_error:
                print(
                    f"Connection error occurred: {conn_error}"
                )
                with self.lock:
                    NebulaStats.failed += 1
            except ValueError as val_error:
                print(
                    f"Value error in response: {val_error}"
                )
                with self.lock:
                    NebulaStats.failed += 1
            except KeyError as key_error:
                print(
                    f"Key error when accessing response data: {key_error}"
                )
                with self.lock:
                    NebulaStats.failed += 1
        else:
            with self.lock:
                NebulaStats.failed += 1
                
class RunTokenJoiner:
    @staticmethod
    def run_joiner(
        utils: Utils,
        invite: str,
        nickname: Optional[str],
        proxy_mode: Optional[str],
        useragent: str,
        delay_min: Optional[int],
        delay_max: Optional[int],
    ) -> None:
        """Run the token joiner with the given configuration."""
        threads = []
        use_proxies = bool(proxy_mode)
        proxy = None

        Nebula = NebulaTokenJoiner(nickname=nickname, _proxy=use_proxies, useragent=useragent)
        NebulaStats.start = time.time()
        threading.Thread(target=title, daemon=True).start()

        for token in utils.get_tokens(formatting=True):
            if use_proxies:
                proxy = utils.get_formatted_proxy("input/proxies.txt")

            thread = threading.Thread(target=Nebula.accept_invite, args=(invite, token, proxy))
            threads.append(thread)
            thread.start()

            if config["delay"]["enabled"]:
                time.sleep(random.uniform(delay_min, delay_max))

        for thread in threads:
            thread.join()

        NebulaStats.thread_running.set()

        RunTokenJoiner.print_summary()

    @staticmethod
    def run_token_filling(
        invite_list: list[str],
        nickname: str,
        proxy_mode: Optional[str],
        useragent: str,
        delay_min: int,
        delay_max: int
    ) -> None:
        """Fill multiple invites using tokens."""
        threads = []
        tokens = Utils.get_tokens(formatting=True)

        if proxy_mode == "per-token":
            token_proxy_map = {
                token: Utils.get_formatted_proxy("input/proxies.txt") for token in tokens
            }
        else:
            token_proxy_map = {}

        NebulaStats.start = time.time()
        threading.Thread(target=title, daemon=True).start()

        for token in tokens:
            proxy = token_proxy_map.get(token) if proxy_mode == "per-token" else None

            thread = threading.Thread(
                target=RunTokenJoiner.handle_token_invites,
                args=(token, invite_list, nickname, proxy_mode, proxy, useragent, delay_min, delay_max),
                daemon=True
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        NebulaStats.thread_running.set()
        RunTokenJoiner.print_summary()

    @staticmethod
    def handle_token_invites(
        token: str,
        invite_list: list[str],
        nickname: str,
        proxy_mode: Optional[str],
        static_proxy: Optional[str],
        useragent: str,
        delay_min: int,
        delay_max: int
    ) -> None:
        """Handle multiple invite joins for a single token."""
        session_id, ws, interval = get_session_id(token)
        if ws:
            print(f"{NebulaColor.GREEN}Connected. Session ID: {session_id}")
            keep_session_alive(ws, interval)
        for invite in invite_list:
            proxy = (
                Utils.get_formatted_proxy("input/proxies.txt")
                if proxy_mode == "rotating"
                else static_proxy
            )

            Nebula = NebulaTokenJoiner(nickname=nickname, _proxy=proxy, useragent=useragent, filling=True)
            Nebula.accept_invite(invite, token, proxy, session_id)

            if config["delay"]["enabled"]:
                time.sleep(random.uniform(delay_min, delay_max))

    @staticmethod
    def print_summary() -> None:
        """Print a summary of the join operation."""
        print(
            f"{NebulaLogging.LC} {NebulaColor.LIGHTBLACK}Joined: {NebulaColor.GREEN}{len(NebulaStats.joined)}"
            f"{NebulaColor.LIGHTBLACK} | Failed: {NebulaColor.RED}{NebulaStats.failed}"
            f"{NebulaColor.LIGHTBLACK} | Total: {red_gradient[2]}{len(NebulaStats.joined) + NebulaStats.failed}{NebulaColor.RESET}"
        )
        input()

def main() -> None:
    """Main function to run the token joiner."""
    utils = Utils()
    discord = Discord()
    xcontext = None

    utils.clear()
    HandleSetup.show_initial_title()

    useragent = HandleSetup.fetch_user_agent()
    intro()

    Utils.new_title("Nebula Token Joiner - v1.1.0")
    proxy_mode = HandleSetup.handle_proxies(utils)

    if config["join"]["token_filling"]:
        invite_list = HandleSetup.get_invite_links()

        HandleSetup.setup_headers(discord=discord, user_agent=useragent)
        nickname = HandleSetup.get_nickname()
        delay_min, delay_max = HandleSetup.get_delay()

        RunTokenJoiner.run_token_filling(
            invite_list, nickname, proxy_mode, useragent, delay_min, delay_max
        )
        return

    invite = HandleSetup.get_invite_link()
    HandleSetup.validate_invite(invite)

    location, guild_id, channel_id, type_ = utils.get_xcontext_values(
        invite=invite,
        token=utils.get_random_token(),
        proxie=proxy_mode
    )

    if guild_id:
        xcontext = (location, guild_id, channel_id, type_)

    HandleSetup.setup_headers(discord=discord, user_agent=useragent, xcontext=xcontext)

    nickname = HandleSetup.get_nickname()
    delay_min, delay_max = HandleSetup.get_delay()

    RunTokenJoiner.run_joiner(
        utils, invite, nickname, proxy_mode, useragent, delay_min, delay_max
    )

if __name__ == "__main__":
    main()

