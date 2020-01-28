# This project is in an alpha state

Primary, the source code of this project is very ugly. Also, there
are some features missing which probably will be implemented in the feature.

# Botblume_Telegram

This is a small telegram bot which interacts with a microcontroller
to query the state of a soil sensor. 
You can use it to monitor your plants and find out, when its again to give them some
water (without the need to get your hands dirty). This is all done via MQTT. 

In order to get the ground's moisture level of your favorite plant, you can simply query
the bot by using the `/wasserstand plantName` command.

_If you remember the alpha notice from the beginning of this readme: Yes, you probably will be able to use a different command prefix then this german one._

## Features

* **Register multiple plants**: You can add as many plants as you want!
* **Add a custom message and photo for each moisture state**: Maximum level of customization!

## Getting started

In order to start this bot, you need to execute the following steps. 

1. **Install the Dependencies**: This project uses `pipenv` to manage the dependencies.
That means in order for you to install and start the project, you need an installation of `pipenv` on your
system. You can simply install it with pip by doing: 

```
pip3 install pipenv
```

After we got this out of the way, we can now start to install the needed dependencies.
This can be done by executing: 

```
pipenv install
```

2. **Obtain a Telegram Api Token**: In order for the bot to work, you need to create a Telegram Api token. This is
well documented in the official telegram documentation: https://core.telegram.org/bots#3-how-do-i-create-a-bot

3. **Add general configuration**: The _general_ configuration is stored as a config file called `config.conf`. 
You need to create this file manually (since I added it to the _.gitignore_ file to prevent to publish my telegram api token).

If you created this file, you have to provide your telegram api token. This can be done by adding

```
telegram_api_token = YOUR_TOKEN
```

to the `config.conf` - file. 

4. **Create a Flowerfile**: A _Flowerfile_ is nothing more then a simple YAML File, which contains all needed information's
about your flowers (aka sensors). To create this file, simply create a text file called `flowers.yaml`. 

In this file, you can configure your flowers like so: 

```yaml
- name: "awesome_flower" # Name of your flower.
  mqtt_id: 1 # Id which is used by the MQTT - Sensor for this specific flower.
  messages: # An array of different messages, which can be set different perceptual ranges.
    - percentage_min: 0
      percentage_max: 19
      message: "Please give me some water soon :("

    - percentage_min: 20
      percentage_max: 79
      message: "Im Fine, no need to worry"

    - percentage_min: 80
      percentage_max: 99
      message: "Im F U L L. Do not give me any additional water pls."
```

_Its actually enough to just specify one message which covers the whole 0 - 99 range_. 


5. **Start your Arduino**: In order to measure the moisture, you need to have an arduino, which also needs
a way to well ...measure the moisture. You can find such application on my _botblume/arduino_ repo. 

6. **Start the Bot**: If you are done, you can start the bot by using the following command: 

```
pipenv run python botblume.py
```

With the example flowerfile from above, you can now query the waterlevel of your flower by 
executing the command `/wasserstand awesome_flower`. 

## Configuration

As you guessed, you can configure a few thing to your likings. 

### General configuration 

The general configuration contains all bot related stuff. All parameters can be set in your `config.conf`
File.

You can configure the following settings: 

* `telegram_api_token`: The api token which is needed to connect to the telegram bot.
* `mqtt_server_address`: The address of the MQTT - Broker which should be used. _Defaults to 127.0.0.1._
* `mqtt_server_port`: The port where the MQTT - Broker is listening on. 
_Defaults to 1887._

All of those settings can also be set by command line arguments. You can
do this by using a double dash as a prefix and a space to delimit the 
parameter name from the value.

If you would like to read some funky debug output, you can also add the `-d` or `--debug` switch. 

### Flower Configuration

The `flowers.yaml` file contains all of the flowers, you want to monitor. 
Each flower has the flowing properties: 

* `name`: A unique name of the flower. This name is used to query the
flower with the `/wasserstand` command.
* `mqtt_id`: A unique identifier which specifies the topic for the listening sensor. 
* `messages`: An array of messages, which should be included in each status
query. You can specify a custom message for each range inside the
interval from 0 to 100. 
  * `percentage_min`: The start of the perceptual range.
  * `percentage_max`: The end of the perceptual range.
  * `message:`: The actual message which should be included.
  * `[include_photo]`: If you also want to include a photo to your message, set this to `true`. 
  * `[photo_path]`: Path to the photo which should be included with your message. 