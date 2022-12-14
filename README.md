# Invicta Integration

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]
[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]

This component enable the control of Invicta Pellet Stoves by Home Assistant.

Tested with the Invicta Fontica 8 pellet stove (not tested on others stoves but should work if the stove uses a Winet Control wifi module)

**This component will set up the following platforms.**

Platform | Description
-- | --
`binary_sensor` | Show something `True` or `False`.
`sensor` | Show info from blueprint API.
`switch` | Switch something `True` or `False`.

![logo][logoimg]

## Installation

1. Using the tool of choice open the directory (folder) for your HA configuration (where you find `configuration.yaml`).
2. If you do not have a `custom_components` directory (folder) there, you need to create it.
3. In the `custom_components` directory (folder) create a new folder called `integration_blueprint`.
4. Download _all_ the files from the `custom_components/integration_blueprint/` directory (folder) in this repository.
5. Place the files you downloaded in the new directory (folder) you created.
6. Restart Home Assistant
7. In the HA UI go to "Configuration" -> "Integrations" click "+" and search for "Integration blueprint"

Using your HA configuration directory (folder) as a starting point you should now also have this:

```text
custom_components/integration_blueprint/translations/en.json
custom_components/integration_blueprint/translations/nb.json
custom_components/integration_blueprint/translations/sensor.nb.json
custom_components/integration_blueprint/__init__.py
custom_components/integration_blueprint/api.py
custom_components/integration_blueprint/binary_sensor.py
custom_components/integration_blueprint/config_flow.py
custom_components/integration_blueprint/const.py
custom_components/integration_blueprint/manifest.json
custom_components/integration_blueprint/sensor.py
custom_components/integration_blueprint/switch.py
```

## Configuration is done in the UI

<!---->

## Contributions are welcome!

If you want to contribute to this please read the [Contribution guidelines](CONTRIBUTING.md)

***

[integration_invicta]: https://github.com/docteurzoidberg/ha-invicta
[buymecoffee]: https://www.buymeacoffee.com/drzoid
[buymecoffeebadge]: https://img.shields.io/badge/buy%20me%20a%20coffee-donate-yellow.svg?style=for-the-badge
[commits-shield]: https://img.shields.io/github/commit-activity/y/docteurzoidberg/ha-invicta.svg?style=for-the-badge
[commits]: https://github.com/docteurzoidberg/ha-invicta/commits/master
[hacs]: https://github.com/custom-components/hacs
[hacsbadge]: https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge
[logoimg]: logo_invicta.png
[license-shield]: https://img.shields.io/github/license/docteurzoidberg/ha-invicta.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-DrZoid-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/docteurzoidberg/ha-invicta.svg?style=for-the-badge
[releases]: https://github.com/docteurzoidberg/ha-invicta/releases
