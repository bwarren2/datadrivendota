from matches.management.tasks.valve_api_calls import RefreshUpdatePlayerPersonas, RefreshPlayerMatchDetail

RefreshUpdatePlayerPersonas().delay()
RefreshPlayerMatchDetail().delay()
