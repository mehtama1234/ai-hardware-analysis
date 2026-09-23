"""Count explicit teaching components, never infer evidence quality from counts."""


def coverage_for(route, papers):
    themes = route['themes']
    return {
        'themes': len(themes),
        'subthemes': sum(len(theme['subthemes']) for theme in themes),
        'worked_themes': sum(bool(theme.get('worked_example')) for theme in themes),
        'practice_themes': sum(bool(theme.get('practice', {}).get('question')) and
                               bool(theme.get('practice', {}).get('answer')) for theme in themes),
        'papers': sum(paper['route'] == route['id'] for paper in papers),
    }
