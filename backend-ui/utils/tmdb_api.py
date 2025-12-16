from utils.utils import api_get_tmdb, api_get

def api_tmdb_search(search_query, page):
    """Récupère les données de TMDB"""
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
        pass
    return search_results


def api_tmdb_get_media(media_id):
    """Récupère les données d'un média de TMDB"""
    try:
        #On récup les genres
        response = api_get('/search/genres?q=&page=1&per_page=100')
        if response.status_code == 200:
            genres_data = response.json()
            genres = genres_data.get('data', [])
        else:
            genres = []

        #on récup les franchises
        response = api_get('/search/franchises?q=&page=1&per_page=100')
        if response.status_code == 200:
            franchises_data = response.json()
            franchises = franchises_data.get('data', [])
        else:
            franchises = None

        #On récup les personnes
        response = api_get('/search/persons?q=&page=1&per_page=100')
        if response.status_code == 200:
            persons_data = response.json()
            persons_api = persons_data.get('data', [])
        else:
            persons_api = None

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
        pass
    return None