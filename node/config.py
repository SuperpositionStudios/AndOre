# Change the key values when going into production. These are a simple but bad way to protect against random
# requests in order to cheat

keys = {
    'node': 'P6rNeO%QnpHoCHdt5Op&G2mqojetESj*gQf*fK!K0uyDjN6XmBblu1S2*fWMCF*77SSOJ2Iy%5!9i&Oor3Lgup8dOhDq^gfOyK!u',
    'master': 'Prsbh%Ul0U6R4ckZEq&iIxGrNY0M#$Fi^TvJuhhZC!E6wt^Sq@whkXWJFS!5iH9f#iPMMp%BFtjP6Eqmz1bN2fi0qllC&^i2TWJ2'
}

production_sleipnir_address = "http://sleipnir.iwanttorule.space"
developing_sleipnir_address = "http://localhost:7100"

developing = True  # Remember to make this False before making a pull request into unstable.

if developing:
    sleipnir_address = developing_sleipnir_address
else:
    sleipnir_address = production_sleipnir_address
