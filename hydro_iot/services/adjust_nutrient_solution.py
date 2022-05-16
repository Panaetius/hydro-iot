from time import monotonic

import inject

from hydro_iot.domain.config import IConfig
from hydro_iot.domain.system_state import SystemState
from hydro_iot.services.ports.event_queue import IEventHub
from hydro_iot.services.ports.logging import ILogging
from hydro_iot.services.ports.message_queue import IMessageQueuePublisher
from hydro_iot.services.ports.pump_gateway import IPumpGateway


@inject.autoparams()
def increase_ph(
    system_state: SystemState,
    logging: ILogging,
    pump_gateway: IPumpGateway,
    message_queue: IMessageQueuePublisher,
    config: IConfig,
):
    if system_state.paused:
        return
    system_state.last_ph_adjustment = monotonic()
    pump_gateway.raise_ph(config.amounts.ph_increase_ml)
    logging.info(f"Increased PH with {config.amounts.ph_increase_ml} ml solution")
    message_queue.send_ph_raised(amount=config.amounts.ph_increase_ml)


@inject.autoparams()
def decrease_ph(
    system_state: SystemState,
    logging: ILogging,
    pump_gateway: IPumpGateway,
    message_queue: IMessageQueuePublisher,
    config: IConfig,
):
    if system_state.paused:
        return
    system_state.last_ph_adjustment = monotonic()
    pump_gateway.lower_ph(config.amounts.ph_decrease_ml)
    logging.info(f"Lowered PH with {config.amounts.ph_decrease_ml} ml solution")
    message_queue.send_ph_lowered(amount=config.amounts.ph_increase_ml)


@inject.autoparams()
def increase_ec(
    system_state: SystemState,
    logging: ILogging,
    pump_gateway: IPumpGateway,
    message_queue: IMessageQueuePublisher,
    config: IConfig,
):
    if system_state.paused:
        return

    if system_state.last_fertilizer_adjustment - monotonic() > config.timings.ec_pump_prime_threshold_s:
        # Prime EC pumps as hoses probably dried up
        pump_gateway.increase_fertilizer(
            flora_grow_ml=5,
            flora_micro_ml=5,
            flora_bloom_ml=5,
        )

    system_state.last_fertilizer_adjustment = monotonic()
    pump_gateway.increase_fertilizer(
        flora_grow_ml=config.amounts.flora_grow_ml,
        flora_micro_ml=config.amounts.flora_micro_ml,
        flora_bloom_ml=config.amounts.flora_bloom_ml,
    )
    logging.info(
        f"Increased EC with {config.amounts.flora_grow_ml}/{config.amounts.flora_micro_ml}/{config.amounts.flora_bloom_ml} ml solution"
    )
    message_queue.send_ec_increased(
        amount_grow=config.amounts.flora_grow_ml,
        amount_micro=config.amounts.flora_micro_ml,
        amount_bloom=config.amounts.flora_bloom_ml,
    )


@inject.autoparams()
def decrease_ec(
    system_state: SystemState,
    logging: ILogging,
    pump_gateway: IPumpGateway,
    message_queue: IMessageQueuePublisher,
    config: IConfig,
):
    if system_state.paused:
        return
    system_state.last_fertilizer_adjustment = monotonic()
    pump_gateway.lower_fertilizer(amount_ml=config.amounts.fresh_water_ml)
    logging.info(f"Decreased EC by adding {config.amounts.fresh_water_ml} ml fresh water.")
    message_queue.send_ec_lowered(amount=config.amounts.fresh_water_ml)


@inject.autoparams()
async def increase_ph_listener(eventhub: IEventHub, logging: ILogging):
    with eventhub.subscribe("ph.up") as queue:
        logging.info("Started listening for ph up events")
        while True:
            _ = await queue.get()
            logging.info("Got increase ph event")
            increase_ph()


@inject.autoparams()
async def decrease_ph_listener(eventhub: IEventHub, logging: ILogging):
    with eventhub.subscribe("ph.down") as queue:
        logging.info("Started listening for ph down events")
        while True:
            _ = await queue.get()
            logging.info("Got decrease ph event")
            decrease_ph()


@inject.autoparams()
async def increase_ec_listener(eventhub: IEventHub, logging: ILogging):
    with eventhub.subscribe("ec.up") as queue:
        logging.info("Started listening for ec up events")
        while True:
            _ = await queue.get()
            logging.info("Got increase ec event")
            increase_ec()


@inject.autoparams()
async def decrease_ec_listener(eventhub: IEventHub, logging: ILogging):
    with eventhub.subscribe("ec.down") as queue:
        logging.info("Started listening for ec down events")
        while True:
            _ = await queue.get()
            logging.info("Got decrease ec event")
            decrease_ec()
