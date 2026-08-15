# Renpho Smart Scale Home Assistant Integration

[![HACS Custom](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/default)
[![Validate](https://github.com/jollyjoyce1995/home-assistant-renpho/actions/workflows/validate.yml/badge.svg)](https://github.com/jollyjoyce1995/home-assistant-renpho/actions/workflows/validate.yml)

A custom Home Assistant integration for **Renpho smart scales**, powered by the [`renpho-api`](https://github.com/danvaneijck/renpho-api) library.

Integrate your Renpho weight and body composition metrics directly into Home Assistant with automatic periodic polling, instant manual refresh, and **full historical data import** into Home Assistant's Long-Term Statistics database.

---

## Features

- ⚖️ **Full Body Composition Metrics**:
  - **Weight** (auto-converts to `kg`, `lbs`, or `st` based on your Home Assistant unit system)
  - **BMI**
  - **Body Fat Percentage**
  - **Body Water Percentage**
  - **Muscle Mass Percentage**
  - **Bone Mass Percentage**
  - **Basal Metabolic Rate (BMR)**
  - **Visceral Fat Level**
  - **Subcutaneous Fat Percentage**
  - **Protein Percentage**
  - **Metabolic / Body Age**
  - **Lean Body Mass (Sinew)**
  - **Fat-Free Weight**
  - **Heart Rate** & **Cardiac Index** (for supported scale models)
  - **Last Measurement Timestamp**
- 📊 **Complete Historical Data Import**: Automatically imports your entire past weigh-in history into Home Assistant's Long-Term Statistics database upon setup, with a dedicated **Import Historical Data** button (`button.renpho_*_import_history`) and `renpho.import_history` service to re-sync anytime.
- 🔄 **Manual Refresh Button**: Trigger an immediate data poll with a dedicated button entity (`button.renpho_*_refresh`).
- ⚙️ **Configurable Polling Interval**: Configure the refresh rate (in minutes) during setup or adjust it anytime in the integration's Options dialog.
- 👥 **Multi-Account Support**: Add `extra_user_ids` if you have linked accounts or multiple Renpho profiles on the same scale.
- 🔒 **Secure Cloud Auth**: Connects directly via encrypted requests to the Renpho Cloud API.

---

## Installation

### Method 1: HACS (Recommended)

1. Open **HACS** in your Home Assistant instance.
2. Go to **Integrations** > click the three dots in the top right > **Custom repositories**.
3. Add `https://github.com/jollyjoyce1995/home-assistant-renpho` with category **Integration**.
4. Click **Download**, then restart Home Assistant.

### Method 2: Manual Installation

1. Download the latest release `.zip` or clone this repository.
2. Copy the `custom_components/renpho` folder into your Home Assistant `<config>/custom_components/` directory.
3. Restart Home Assistant.

---

## Configuration

1. In Home Assistant, go to **Settings** > **Devices & Services**.
2. Click **Add Integration** and search for **Renpho**.
3. Enter your **Email** and **Password** (the same credentials used in the Renpho mobile app).
4. Optionally adjust the **Refresh interval** (default: 60 minutes).
5. Click **Submit**.

Upon setup, your historical measurements are automatically imported in the background into Home Assistant's Long-Term Statistics database.

### Options & Reconfiguration

Click **Configure** on the Renpho integration card to:
- Adjust the polling interval (from 5 to 1440 minutes).
- Specify extra user IDs for multi-profile scale tracking.

---

## Entities Provided

| Entity | Type | Unit | Description |
|---|---|---|---|
| `sensor.renpho_weight` | Sensor | `kg` / `lbs` | Current weight |
| `sensor.renpho_bmi` | Sensor | - | Body Mass Index |
| `sensor.renpho_body_fat` | Sensor | `%` | Body Fat Percentage |
| `sensor.renpho_body_water` | Sensor | `%` | Body Water Percentage |
| `sensor.renpho_muscle_mass` | Sensor | `%` | Skeletal / Muscle Mass |
| `sensor.renpho_bone_mass` | Sensor | `%` | Bone Mass Percentage |
| `sensor.renpho_basal_metabolic_rate` | Sensor | `kcal` | BMR |
| `sensor.renpho_visceral_fat` | Sensor | - | Visceral Fat Level |
| `sensor.renpho_subcutaneous_fat` | Sensor | `%` | Subcutaneous Fat |
| `sensor.renpho_protein` | Sensor | `%` | Protein Percentage |
| `sensor.renpho_body_age` | Sensor | `years` | Metabolic Body Age |
| `sensor.renpho_lean_body_mass` | Sensor | `kg` / `lbs` | Lean Body Mass |
| `sensor.renpho_fat_free_weight` | Sensor | `kg` / `lbs` | Fat Free Weight |
| `sensor.renpho_heart_rate` | Sensor | `bpm` | Heart Rate (if supported) |
| `sensor.renpho_cardiac_index` | Sensor | - | Cardiac Index (if supported) |
| `sensor.renpho_last_measurement` | Sensor | `timestamp` | Time of latest measurement |
| `button.renpho_refresh` | Button | - | Trigger immediate measurement poll |
| `button.renpho_import_history` | Button | - | Import complete account history into Long-Term Statistics |

---

## Long-Term Statistics Dashboard Card Example

You can graph your full historical data using Home Assistant's native **Statistics Graph Card**:

```yaml
type: statistics-graph
title: Weight & Body Fat History
entities:
  - sensor.renpho_weight
  - sensor.renpho_body_fat
stat_types:
  - mean
  - min
  - max
days_to_show: 365
chart_type: line
```

---

## Services

### `renpho.import_history`
Fetches complete historical measurement data from the Renpho cloud and backfills it into Home Assistant Long-Term Statistics.

**Parameters**:
- `entry_id` *(optional)*: Specify a config entry ID. If omitted, imports history for all configured Renpho accounts.

---

## Automations Example

Notify your phone when a new weight measurement is recorded:

```yaml
alias: "Renpho: Weight Measurement Recorded"
trigger:
  - platform: state
    entity_id: sensor.renpho_weight
condition:
  - condition: template
    value_template: "{{ trigger.from_state.state != trigger.to_state.state }}"
action:
  - action: notify.mobile_app_my_phone
    data:
      title: "New Weight Recorded"
      message: "Weight: {{ states('sensor.renpho_weight') }} {{ state_attr('sensor.renpho_weight', 'unit_of_measurement') }} (Body Fat: {{ states('sensor.renpho_body_fat') }}%)"
```

---

## License

MIT License. See [LICENSE](LICENSE) for details.
