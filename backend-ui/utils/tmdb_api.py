from utils.utils_api import api_get_tmdb, api_search

#Recherche sur TMDB de film
def api_tmdb_search_film(search_query, page):
    try:
        response = api_get_tmdb(f'/search/movie?query={search_query}&include_adult=false&language=fr-FR&page={page}')
        if response.status_code == 200:
            data = response.json()

            search_results = {'data': [], 'pagination': {}}
            
            for result in data['results']:
                search_results['data'].append({
                    'id': result['id'],
                    'title': result['title'],
                    'type': 'film',
                    'release_year': result['release_date'][:4],
                    'synopsis': result['overview'],
                    'cover_image_url': f"https://image.tmdb.org/t/p/original{result['poster_path']}",
                })

            search_results['pagination'] = {
                'page': data['page'],
                'per_page': len(data['results']),
                'total': data['total_results'],
                'pages': data['total_pages'],
            }
    except:
        search_results = []
    return search_results


#Recupère un film dans TMDB
def api_tmdb_get_film(media_id):
    try:
        genres, _ = api_search('genres', '', 1, 100)
        if not genres:
            genres = []

        franchises, _ = api_search('franchises', '', 1, 100)
        if not franchises:
            franchises = []

        persons_api, _ = api_search('persons', '', 1, 100)
        if not persons_api:
            persons_api = []

        #on récup le média de tmdb
        response = api_get_tmdb(f'/movie/{media_id}?language=fr-FR')
        if response.status_code == 200:
            data = response.json()

            #TRAITEMENT GENRES
            data_genres = [g['name'] for g in data['genres']]
            result_genres = []
            for genre in genres:
                if genre['name'] in data_genres:
                    result_genres.append(genre['id'])

            #TRAITEMENT FRANCHISES
            try:
                data_franchises = data['belongs_to_collection']['name']
                result_franchises = None
                for franchise in franchises:    
                    if franchise['name'] in data_franchises:
                        result_franchises = franchise['id']
            except:
                result_franchises = None

            #TRAITEMENT TRAILER
            try:
                data_trailer = api_get_tmdb(f'/movie/{media_id}/videos?language=fr-FR')
                result_trailer = None
                if data_trailer.status_code == 200:
                    data_trailer = data_trailer.json()
                    if data_trailer['results'][0]["site"] == "YouTube":
                        result_trailer = f"https://www.youtube.com/embed/{data_trailer['results'][0]['key']}"
            except:
                result_trailer = None

            #TRAITEMENT PERSONNES
            response_persons = api_get_tmdb(f'/movie/{media_id}/credits?language=fr-FR')
            if response_persons.status_code == 200:
                persons_data = response_persons.json()
                persons_tmdb = persons_data.get('cast', [])

                result_persons = []
                for person in persons_tmdb:
                    for person_api in persons_api:
                        if person['name'].lower() == person_api['name'].lower():
                            result_persons.append({
                                'person_id': person_api['id'],
                                'role': 'Acteur' if person['known_for_department'] == 'Acting' else person['known_for_department'],
                                'character_name': person['character'],
                            })
                            break
            
            media_data = {
                'id': data['id'],
                'title': data['title'],
                'media_type': 'film',
                'release_year': data['release_date'][:4],
                'synopsis': data['overview'],
                'cover_image_url': f"https://image.tmdb.org/t/p/original{data['poster_path']}",
                'duration': data['runtime'],
                'genres': result_genres,
                'franchise_id': result_franchises,
                'persons': result_persons,
                'trailer_url': result_trailer,
            }

            return media_data
    except:
        return None
    return None





#Recherche sur TMDB de série
def api_tmdb_search_series(search_query, page):
    try:
        response = api_get_tmdb(f'/search/tv?query={search_query}&include_adult=false&language=fr-FR&page={page}')
        if response.status_code == 200:
            data = response.json()

            search_results = {'data': [], 'pagination': {}}
            
            for result in data['results']:
                search_results['data'].append({
                    'id': result['id'],
                    'title': result['name'],
                    'type': 'serie',
                    'release_year': result['first_air_date'][:4],
                    'synopsis': result['overview'],
                    'cover_image_url': f"https://image.tmdb.org/t/p/original{result['poster_path']}",
                })

            search_results['pagination'] = {
                'page': data['page'],
                'per_page': len(data['results']),
                'total': data['total_results'],
                'pages': data['total_pages'],
            }
    except:
        search_results = []
    return search_results

#Recupère une série dans TMDB
def api_tmdb_get_series(media_id):
    try:
        genres, _ = api_search('genres', '', 1, 100)
        if not genres:
            genres = []

        franchises, _ = api_search('franchises', '', 1, 100)
        if not franchises:
            franchises = []

        persons_api, _ = api_search('persons', '', 1, 100)
        if not persons_api:
            persons_api = []

        #on récup le média de tmdb
        response = api_get_tmdb(f'/tv/{media_id}?language=fr-FR')
        if response.status_code == 200:
            data = response.json()

            #TRAITEMENT GENRES
            data_genres = [g['name'] for g in data['genres']]
            result_genres = []
            for genre in genres:
                if genre['name'] in data_genres:
                    result_genres.append(genre['id'])

            #TRAITEMENT TRAILER
            try:
                data_trailer = api_get_tmdb(f'/tv/{media_id}/videos?language=fr-FR')
                result_trailer = None
                if data_trailer.status_code == 200:
                    data_trailer = data_trailer.json()
                    if data_trailer['results'][0]["site"] == "YouTube":
                        result_trailer = f"https://www.youtube.com/embed/{data_trailer['results'][0]['key']}"
            except:
                result_trailer = None

            #TRAITEMENT PERSONNES
            response_persons = api_get_tmdb(f'/tv/{media_id}/credits?language=fr-FR')
            if response_persons.status_code == 200:
                persons_data = response_persons.json()
                persons_tmdb = persons_data.get('cast', [])

                result_persons = []
                for person in persons_tmdb:
                    for person_api in persons_api:
                        if person['name'].lower() == person_api['name'].lower():
                            result_persons.append({
                                'person_id': person_api['id'],
                                'role': 'Acteur' if person['known_for_department'] == 'Acting' else person['known_for_department'],
                                'character_name': person['character'],
                            })
                            break
            
            media_data = {
                'id': data['id'],
                'title': data['name'],
                'media_type': 'serie',
                'release_year': data['first_air_date'][:4],
                'synopsis': data['overview'],
                'cover_image_url': f"https://image.tmdb.org/t/p/original{data['poster_path']}",
                'genres': result_genres,
                'persons': result_persons,
                'trailer_url': result_trailer,
            }

            return media_data
    except:
        return None
    return None
