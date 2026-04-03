import pytest
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Mots-clés haineux à détecter
HATE_KEYWORDS = ["haine", "racisme", "insulte", "violence", "hate", "kill", "nazi"]

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # En CI, on utilise le chromedriver fourni par setup-chrome
    # En local, on utilise webdriver-manager
    chromedriver_path = os.environ.get("CHROMEDRIVER_PATH")
    if chromedriver_path:
        service = Service(chromedriver_path)
    else:
        from webdriver_manager.chrome import ChromeDriverManager
        service = Service(ChromeDriverManager().install())

    driver = webdriver.Chrome(service=service, options=options)
    driver.get("https://www.reddit.com/r/popular/")
    time.sleep(3)
    yield driver
    driver.quit()

def get_post_titles(driver):
    """Récupère les titres des 10 premiers posts visibles."""
    try:
        posts = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[data-click-id='body']"))
        )
        return posts[:10]
    except Exception:
        # Sélecteur alternatif si Reddit change son HTML
        posts = driver.find_elements(By.CSS_SELECTOR, "h3")
        return posts[:10]

def test_titres_sans_contenu_haineux(driver):
    """Test 1 : Vérifie l'absence de mots-clés haineux dans les titres des 10 posts."""
    posts = get_post_titles(driver)
    assert len(posts) > 0, "Aucun post trouvé sur la page"
    titres_verifies = []
    for post in posts:
        title = post.text.lower()
        titres_verifies.append(f"✔ Titre vérifié : {post.text[:80]}")
        assert not any(kw in title for kw in HATE_KEYWORDS), \
            f"⚠ Contenu haineux détecté dans le titre : {title}"
    print("\n".join(titres_verifies))

def test_corps_sans_contenu_haineux(driver):
    """Test 2 : Vérifie l'absence de mots-clés haineux dans le corps des 10 posts."""
    posts = get_post_titles(driver)
    assert len(posts) > 0, "Aucun post trouvé sur la page"
    for i, post in enumerate(posts):
        titre = post.text[:60]
        try:
            post.click()
            time.sleep(2)
            # Cherche le contenu textuel du post
            body_elements = driver.find_elements(
                By.CSS_SELECTOR, "[data-testid='post-content'], .RichTextJSON-root, [slot='text-body']"
            )
            body = " ".join([el.text for el in body_elements]).lower()
            assert not any(kw in body for kw in HATE_KEYWORDS), \
                f"⚠ Contenu haineux dans le corps du post '{titre}'"
            print(f"✔ Corps vérifié pour : {titre}")
        except Exception as e:
            print(f"⚠ Impossible d'ouvrir le post {i+1} : {e}")
        finally:
            driver.back()
            time.sleep(2)

def test_bouton_signalement_present(driver):
    """Test 3 : Vérifie la présence d'un bouton de signalement sur chaque post."""
    posts = get_post_titles(driver)
    assert len(posts) > 0, "Aucun post trouvé sur la page"
    for i, post in enumerate(posts):
        titre = post.text[:60]
        try:
            post.click()
            time.sleep(2)
            # Cherche le bouton "Report" ou "Signaler"
            boutons = driver.find_elements(
                By.XPATH,
                "//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                "'abcdefghijklmnopqrstuvwxyz'), 'report') or "
                "contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
                "'abcdefghijklmnopqrstuvwxyz'), 'signaler')]"
            )
            assert len(boutons) > 0, \
                f"⚠ Bouton de signalement absent pour : {titre}"
            print(f"✔ Bouton signalement présent pour : {titre}")
        except AssertionError:
            raise
        except Exception as e:
            print(f"⚠ Erreur sur le post {i+1} : {e}")
        finally:
            driver.back()
            time.sleep(2)