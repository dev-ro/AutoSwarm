import pytest

def test_uv_dependencies_resolvable():
    """
    Test that all major dependencies migrated from requirements.txt to pyproject.toml (uv)
    are successfully installed and accessible in the environment.
    """
    # Core framework
    import agno

    # Google and Gemini
    import google.generativeai
    import googleapiclient
    import google_auth_httplib2
    import google_auth_oauthlib

    # Web & Scraping
    import playwright
    import bs4

    # Social Media / API clients
    import tweepy
    import praw
    import atproto
    import substack

    # Utilities
    import dotenv
    import termcolor
    import texttable

    assert True, "All critical dependencies resolved successfully."
