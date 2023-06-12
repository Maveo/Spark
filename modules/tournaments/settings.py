from imagestack_svg.imageresolve import ImageStackResolveString

from helpers.settings_manager import Setting

ko_tournament_image = ImageStackResolveString('''
{% if rounds[0][0][0] is not none %}
    <rect x="0" y="0" width="400" height="40" rx="0" ry="0" fill="rgb(48, 50, 55)" />
    <text x="0" y="30" text-anchor="start" font-family="Calibri" font-size="30" fill="rgb(255, 255, 255)">Winner: {{ rounds[0][0][0] }}</text>
{% endif %}
{% set rounds_len = (rounds | length) - 1 %}
{% for round in rounds[1:] %}
    {% set round_i = loop.index %}
    {% set y = round_i * 110 %}
    {% for i in range(0, round | length, 2) %}
        {% set x = i * (2 ** (rounds_len - round_i)) * 110 + ((2 ** (rounds_len - round_i - 1)) - 0.5) * 220 %}
        <rect x="{{x}}" y="{{y}}" width="200" height="100" rx="20" ry="20" fill="rgb(48, 50, 55)" />
        <text x="{{x + 20}}" y="{{y + 30}}" text-anchor="start" font-family="Calibri" font-size="14" fill="rgb(255, 255, 255)">{{ round[i][0][:20] if round[i][0] is not none }}</text>
        <text x="{{x + 20}}" y="{{y + 80}}" text-anchor="start" font-family="Calibri" font-size="14" fill="rgb(255, 255, 255)">{{ round[i+1][0][:20] if round[i+1][0] is not none }}</text>
        {% if round[i][1] is not none %}
            <text x="{{x + 180}}" y="{{y + 30}}" text-anchor="end" font-family="Calibri" font-size="14" font-weight="bold" fill="rgb(255, 255, 255)">{{ round[i][1] }}</text>
            <text x="{{x + 180}}" y="{{y + 80}}" text-anchor="end" font-family="Calibri" font-size="14" font-weight="bold" fill="rgb(255, 255, 255)">{{ round[i+1][1] }}</text>
        {% endif %}
        <line x1="{{x}}" y1="{{y + 50}}" x2="{{x + 200}}" y2="{{y + 50}}" stroke="rgb(255, 255, 255)" />
    {% endfor %}
{% endfor %}
''')

SETTINGS = {
    'KO_TOURNAMENT_IMAGE': Setting(
        value=ko_tournament_image,
        description='Template to create a KO tournament',
        itype='text',
        categories=['Image'],
        preview_call='ko-tournament-image'
    ),
}
