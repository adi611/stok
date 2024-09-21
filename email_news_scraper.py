import os
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup

load_dotenv()

@dataclass
class Story:
    title: str
    time: str
    url: str

class Scraper(ABC):
    @abstractmethod
    def scrape(self) -> List[Story]:
        pass

class WebsiteScraper(Scraper):
    def __init__(self, url: str):
        self.base_url = url

    def scrape(self) -> List[Story]:
        response = requests.get(self.base_url)
        soup = BeautifulSoup(response.text, "html.parser")
        story_divs = soup.select(
            "body main.pageHolder div.main_container section.section_list div.tabdata div.eachStory"
        )

        stories = []
        for div in story_divs:
            title = div.find("h3").find("a").text.strip()
            time = div.find("time").text.strip()
            url = div.find("h3").find("a")["href"]
            full_url = f"{self.base_url.rstrip('/')}/{url.lstrip('/')}"
            stories.append(Story(title, time, full_url))

        return stories

class StoryFilter:
    @staticmethod
    def filter_stories(stories: List[Story], keywords: List[str]) -> List[Story]:
        return [
            story
            for story in stories
            if any(keyword in story.title.lower() for keyword in keywords)
        ]

class MessageSender(ABC):
    @abstractmethod
    def send_message(self, story: Story) -> bool:
        pass

class MailgunSender(MessageSender):
    def __init__(self, api_key: str, domain: str, from_email: str, to_email: str):
        self.api_key = api_key
        self.domain = domain
        self.from_email = from_email
        self.to_email = to_email
        self.base_url = f"https://api.mailgun.net/v3/{domain}/messages"

    def send_message(self, story: Story) -> bool:
        subject = f"News Alert: {story.title}"
        body = f"""
        Title: {story.title}
        Time: {story.time}
        URL: {story.url}
        """

        try:
            response = requests.post(
                self.base_url,
                auth=("api", self.api_key),
                data={
                    "from": self.from_email,
                    "to": self.to_email,
                    "subject": subject,
                    "text": body
                }
            )
            response.raise_for_status()
            print(f"Message sent successfully for story: {story.title}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error sending message: {e}")
            return False

class StoryProcessor:
    def __init__(self, scraper: Scraper, filter: StoryFilter, sender: MessageSender):
        self.scraper = scraper
        self.filter = filter
        self.sender = sender

    def process(self, keywords: List[str]):
        stories = self.scraper.scrape()
        filtered_stories = self.filter.filter_stories(stories, keywords)

        try:
            for story in filtered_stories:
                self.sender.send_message(story)
        except Exception as e:
            print(f"An error occurred while processing stories: {e}")

def main():
    url = os.getenv("WEBSITE_URL")
    mailgun_api_key = os.getenv("MAILGUN_API_KEY")
    mailgun_domain = os.getenv("MAILGUN_DOMAIN")
    from_email = os.getenv("FROM_EMAIL")
    to_email = os.getenv("TO_EMAIL")

    scraper = WebsiteScraper(url)
    filter = StoryFilter()
    sender = MailgunSender(mailgun_api_key, mailgun_domain, from_email, to_email)
    processor = StoryProcessor(scraper, filter, sender)

    processor.process(keywords=["bonus", "split"])

if __name__ == "__main__":
    main()