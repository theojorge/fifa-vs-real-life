from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import time
import pandas as pd

def get_player_data_from_futbin(player_name: str) -> list:
    # Configuración Chrome headless para Colab / Linux
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome(options=chrome_options)

    try:
        link = f'https://www.futbin.com/players?search={player_name}&showStats=Age%2CWeight&gender=men'
        driver.get(link)
        time.sleep(1)  # Esperar a que cargue la página

        # Listas para guardar datos
        names = []
        ratings = []
        strongfoot = []
        weakfoot = []
        position = []
        sidePosition = []
        skill_moves = []
        pace = []
        shooting = []
        passing = []
        dribbling = []
        defending = []
        physic = []
        body = []
        age = []
        weight = []
        price = []
        league = []
        card_type = []
        links = []
        
        tbody_rows = driver.find_elements(By.CLASS_NAME, 'player-row')
        for row in tbody_rows:
            
            try:
                anchor_tags = row.find_elements(By.TAG_NAME, 'a')
                if anchor_tags:
                    found_player_link = False
                    for anchor in anchor_tags:
                        href = anchor.get_attribute('href')
                        if href and 'player' in href.lower():  
                            links.append(href)
                            found_player_link = True
                            break
                    if not found_player_link:
                        print("No relevant player link found in anchor tags")
                        links.append(None)
                else:
                    print("No anchor tags found in the row")
                    links.append(None)
            except Exception as e:
                    print(f"Error while searching for anchor tags: {str(e)}")
                    links.append(None)
          
            names.append(row.find_element(By.CLASS_NAME, 'table-player-name').text)
            print(names[-1])
            ratings.append(row.find_element(By.CLASS_NAME, 'player-rating-card-text').text)
            position.append(row.find_element(By.CLASS_NAME, 'table-pos-main').text)
            try:
                sidePosition.append(row.find_element(By.CLASS_NAME, 'table-pos').find_element(By.CLASS_NAME, 'text-faded').text)
            except:
                sidePosition.append('')
            price.append(row.find_element(By.CLASS_NAME, 'price').text)
            weakfoot.append(row.find_element(By.CLASS_NAME, 'table-weak-foot').text)
            card_type.append(row.find_element(By.CLASS_NAME, 'table-player-revision').text)
            skill_moves.append(row.find_element(By.CLASS_NAME, 'table-skills').text)
            pace.append(row.find_element(By.CLASS_NAME, 'table-key-stats').text)
            shooting.append(row.find_element(By.CLASS_NAME, 'table-shooting').text)
            passing.append(row.find_element(By.CLASS_NAME, 'table-passing').text)
            dribbling.append(row.find_element(By.CLASS_NAME, 'table-dribbling').text)
            defending.append(row.find_element(By.CLASS_NAME, 'table-defending').text)
            physic.append(row.find_element(By.CLASS_NAME, 'table-physicality').text)
            body.append(row.find_element(By.CLASS_NAME, 'table-height').text)
            age.append(row.find_element(By.CLASS_NAME, 'table-age').text)
            weight.append(row.find_element(By.CLASS_NAME, 'table-weight').text)
            league.append(row.find_element(By.CLASS_NAME, 'table-player-league').find_element(By.TAG_NAME, 'img').get_attribute('title'))
            
            player_strongfoot = row.find_element(By.CLASS_NAME, 'table-foot').find_element(By.TAG_NAME, 'img').get_attribute('src')
            if 'right' in player_strongfoot.lower():
                strongfoot.append('Right')
            else:
                strongfoot.append('Left')

        # Crear DataFrame
        players_df = pd.DataFrame({
            'Name': names,
            'overall_rating': ratings,
            'Position': position,
            'Side Position': sidePosition,
            'price': price,
            'weak_foot': weakfoot,
            'skill_moves': skill_moves,
            'pace': pace,
            'shooting': shooting,
            'passing': passing,
            'dribbling': dribbling,
            'defending': defending,
            'physic': physic,
            'Body Type': body,
            'age': age,
            'weight_kg': weight,
            'preferred_foot': strongfoot,
            'club_league_name': league,
            'card': card_type,
            'link': links,
        })
        players_df['positions'] = (
            players_df['Position'].str.replace(r'\+\+', '', regex=True).str.strip() + ', ' + 
            players_df['Side Position'].str.replace(r'\+\+', '', regex=True).str.replace(r'\s*,\s*', ', ', regex=True).str.strip()
        ).str.strip(', ')
        
        players_df = players_df.drop(['Position', 'Side Position'], axis=1)
        
        # Limpiar columnas numéricas y convertir tipos
        players_df['height_cm'] = players_df['Body Type'].str.split('|').str[0].str.strip().str.replace('cm', '').astype(int)
        players_df['weight_kg'] = players_df['weight_kg'].str.replace('kg', '').astype(int)
        players_df = players_df.drop(columns=['Body Type'])
        
        numeric_cols = ['age', 'height_cm', 'weight_kg', 'weak_foot', 'skill_moves',
                        'overall_rating', 'pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic']

        for col in numeric_cols:
            players_df[col] = pd.to_numeric(players_df[col], errors='coerce')


        # Finalmente armar la lista con la estructura que quieres
        result = []
        for idx, row in players_df.iterrows():
            features = {
                "player_id": idx, 
                "club_league_name": row['club_league_name'],
                "preferred_foot": row['preferred_foot'],
                "positions": row['positions'],
                "height_cm": row['height_cm'],
                "weight_kg": row['weight_kg'],
                "weak_foot": row['weak_foot'],
                "skill_moves": row['skill_moves'],
                "overall_rating": row['overall_rating'],
                "age": row['age'],
                "pace": row['pace'],
                "shooting": row['shooting'],
                "passing": row['passing'],
                "dribbling": row['dribbling'],
                "defending": row['defending'],
                "physic": row['physic'],
            }
            meta = {
                "player_id": idx,
                "Name": row['Name'],
                "card": row['card'],
                "price": row['price'],
                "link": row['link'],
            }
            result.append({"features": features, "meta": meta})
        return result

    finally:
        driver.quit()
