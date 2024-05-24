from playwright.sync_api import Playwright, sync_playwright
from random import randint
import datetime
import time
import json


def get_input_language():
    while True:
        print("What is your language? (English:1, Italiano:2)")
        language = input("Please enter the number corresponding to your language: ")

        if language in ['1', '2']:
            return int(language)
        else:
            print("Invalid input. Please input 1 or 2.")


def get_time_to_start():
    time_to_start = input("Time to Start (in seconds)? (Default 50 seconds): ")
    if not time_to_start.strip():
        time_to_start = 50
    else:
        time_to_start = int(time_to_start)
    return time_to_start


def restrict_message_not_displayed(page, language):
    if language == 1:
        return not page.get_by_text('Try Again Later').is_visible() and not page.get_by_text(
            'Please wait a few minutes before you try again').is_visible()

    if language == 2:
        return not page.get_by_text('Riprova pi').is_visible() and not page.get_by_text(
            'Limitiamo la frequenza con').is_visible() and not page.get_by_text(
            'Attendi qualche minuto prima di riprovare').is_visible()


def get_button_name(language):
    if language == 1:
        return 'Follow'

    if language == 2:
        return 'Segui'


def store_context(browser):
    try:
        with open('state.json', 'r') as file:
            storage_state = json.load(file)
            return browser.new_context(storage_state=storage_state)

    except:
        return browser.new_context()


def iterate_and_wait(page, time_to_start):
    for x in range(time_to_start):
        print(f'{time_to_start - x} seconds to start script')
        page.wait_for_timeout(1000)


def usernames(page):
    return page.query_selector_all(
        '.x1dm5mii.x16mil14.xiojian.x1yutycm.x1lliihq.x193iq5w.xh8yej3 .x1i10hfl.xjbqb8w.x1ejq31n.xd10rxx.x1sy0etr.x17r0tee.x972fbf.xcfux6l.x1qhh985.xm0m39n')


def get_follow_button(context):
    pages = context.pages

    if len(pages) == 1:
        context.pages[0].wait_for_timeout(4000)

    if len(pages) == 3:
        context.pages[2].close()
        context.pages[0].wait_for_timeout(1000)

    if len(pages) == 4:
        context.pages[2].close()
        context.pages[3].close()
        context.pages[0].wait_for_timeout(1000)

    page1 = context.pages[1]
    page1.bring_to_front()

    locator = page1.locator('section.x1xdureb.x1agbcgv.x1wo17tc button._acan._acap._aj1-._ap30')
    return locator, page1


def do_large_scroll(page, input_language):
    buttons = page.query_selector_all('button._acan._acap._acas._aj1-._ap30')
    has_one_follow = any(button.inner_text() == get_button_name(input_language) for button in buttons)

    if not has_one_follow:
        print('We dont have any follow buttons')
        time.sleep(3)
        page.mouse.wheel(0, 15000)


def run(playwright: Playwright) -> None:

    time_to_start = get_time_to_start()
    input_language = get_input_language()

    browser = playwright.chromium.launch(headless=False)
    context = store_context(browser)

    page = context.new_page()
    page.goto("https://www.instagram.com/", timeout=200000)

    iterate_and_wait(page, time_to_start)

    context.storage_state(path='state.json')
    clicked_followers = set()

    while restrict_message_not_displayed(page, input_language):
        do_large_scroll(page, input_language)

        for username in usernames(page):
            if username.inner_text() in clicked_followers:
                continue

            clicked_followers.add(username.inner_text())
            username.click(modifiers=["Control"])
            page.wait_for_timeout(2000)

            try:
                button, page1 = get_follow_button(context)

                page1.wait_for_timeout(randint(3000, 3300))

                if get_button_name(input_language) == button.inner_text(timeout=3000):
                    button.click()
                    page.wait_for_timeout(randint(3000, 3500))

                if not restrict_message_not_displayed(page, input_language):
                    page1.close()
                    break

                page1.close()

            except Exception as e:
                page1.close()

            page.bring_to_front()
            page.mouse.wheel(0, 65)

    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
