import asyncio
import os
import sys
from playwright.async_api import async_playwright

BASE_URL = "http://127.0.0.1:8080"
SCREENSHOT_DIR = os.path.abspath("docs/screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

async def capture_all():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        
        page_errors = []
        console_errors = []

        # Viewports to test
        viewports = [
            {"name": "1440px", "width": 1440, "height": 900},
            {"name": "390px", "width": 390, "height": 844}
        ]

        for vp in viewports:
            print(f"\n=================== TESTING VIEWPORT {vp['name']} ===================")
            context = await browser.new_context(viewport={"width": vp["width"], "height": vp["height"]})
            page = await context.new_page()

            page.on("pageerror", lambda err: page_errors.append(str(err)))
            page.on("console", lambda msg: console_errors.append(f"[{msg.type}] {msg.text}") if msg.type in ["error", "warning"] else None)

            # 1. Capture Auth Screen before login
            await page.goto(BASE_URL, wait_until="networkidle")
            await asyncio.sleep(1)

            # Assert no JS errors on initial page load
            js_type = await page.evaluate("typeof ShamixApi")
            print(f"[{vp['name']}] typeof ShamixApi: {js_type}")
            if js_type != "object":
                raise RuntimeError(f"ShamixApi is not defined! Got typeof ShamixApi = {js_type}")

            # Capture Auth Screenshot
            auth_path = os.path.join(SCREENSHOT_DIR, f"01-auth-{vp['name']}.png")
            await page.screenshot(path=auth_path)
            print(f"Saved: {auth_path}")

            # 2. Perform Login as demo / Demo12345!
            print(f"[{vp['name']}] Logging in as demo / Demo12345!...")
            await page.fill("#login-username", "demo")
            await page.fill("#login-password", "Demo12345!")
            await page.click("#login-submit-btn")

            # Wait for logged in state
            await page.wait_for_selector("#app-container:not(.hidden)", timeout=10000)
            await asyncio.sleep(1.5)

            # Helper verification function
            async def assert_clean_screen(screen_name):
                content = await page.content()
                if "is not defined" in content:
                    raise RuntimeError(f"Failing loudly: Screen {screen_name} contains 'is not defined' JS error text!")
                is_auth_hidden = await page.eval_on_selector("#view-auth", "el => el.classList.contains('hidden')")
                if not is_auth_hidden:
                    raise RuntimeError(f"Failing loudly: Screen {screen_name} still shows login form!")

            # 1. Dashboard
            await page.evaluate("navigateTo('dashboard')")
            await asyncio.sleep(1)
            await assert_clean_screen("dashboard")
            await page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"dashboard-{vp['name']}.png"))
            print(f"[{vp['name']}] Captured & verified screen 'dashboard'")

            # 2. Lessons
            await page.evaluate("navigateTo('lessons')")
            await asyncio.sleep(1)
            await assert_clean_screen("lessons")
            await page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"lessons-{vp['name']}.png"))
            print(f"[{vp['name']}] Captured & verified screen 'lessons'")

            # 3. Lesson Modal
            await page.evaluate("openLessonModal('les-1')")
            await asyncio.sleep(1)
            await assert_clean_screen("lesson-modal")
            await page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"lesson-modal-{vp['name']}.png"))
            print(f"[{vp['name']}] Captured & verified screen 'lesson-modal'")
            await page.evaluate("closeLessonModal()")
            await asyncio.sleep(0.5)

            # 4. Homework
            await page.evaluate("navigateTo('homework')")
            await asyncio.sleep(1)
            await assert_clean_screen("homework")
            await page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"homework-{vp['name']}.png"))
            print(f"[{vp['name']}] Captured & verified screen 'homework'")

            # 5. Quiz Modal
            await page.evaluate("startQuiz('hw-1')")
            await asyncio.sleep(1)
            await assert_clean_screen("quiz-modal")
            await page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"quiz-modal-{vp['name']}.png"))
            print(f"[{vp['name']}] Captured & verified screen 'quiz-modal'")
            await page.evaluate("closeQuizModal()")
            await asyncio.sleep(0.5)

            # 6. Leaderboard
            await page.evaluate("navigateTo('leaderboard')")
            await asyncio.sleep(1)
            await assert_clean_screen("leaderboard")
            await page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"leaderboard-{vp['name']}.png"))
            print(f"[{vp['name']}] Captured & verified screen 'leaderboard'")

            # 7. Attendance
            await page.evaluate("navigateTo('attendance')")
            await asyncio.sleep(1)
            await assert_clean_screen("attendance")
            await page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"attendance-{vp['name']}.png"))
            print(f"[{vp['name']}] Captured & verified screen 'attendance'")

            # 8. Flashcards
            await page.evaluate("navigateTo('flashcards')")
            await asyncio.sleep(1)
            await assert_clean_screen("flashcards")
            await page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"flashcards-{vp['name']}.png"))
            print(f"[{vp['name']}] Captured & verified screen 'flashcards'")

            # 9. Badges
            await page.evaluate("navigateTo('badges')")
            await asyncio.sleep(1)
            await assert_clean_screen("badges")
            await page.screenshot(path=os.path.join(SCREENSHOT_DIR, f"badges-{vp['name']}.png"))
            print(f"[{vp['name']}] Captured & verified screen 'badges'")

            await context.close()

        print("\n=================== BROWSER CONSOLE LOGS & ERRORS ===================")
        print(f"Page errors: {page_errors}")
        print(f"Console errors/warnings: {console_errors}")

        if page_errors:
            raise RuntimeError(f"Page error detected during execution: {page_errors}")

        await browser.close()
        print("\nSUCCESS: All authenticated screenshots captured and verified cleanly!")

if __name__ == "__main__":
    asyncio.run(capture_all())
