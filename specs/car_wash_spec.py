# -*- coding: utf-8 -*-

from mamba import *
from hamcrest import *
from doublex import *

from car_wash import CarWashService, CarWashJob, Car, Customer, InMemoryJobRepository

def create_car_wash_service(notifier, repository):
    return CarWashService(notifier, repository)


car1 = Car(plate='123-XXX')
car2 = Car(plate='666-XXX')
car3 = Car(plate='777-XXX')
customer1 = Customer(name='customer1', mobile_phone='123')
customer2 = Customer(name='customer2', mobile_phone='666')
customer3 = Customer(name='customer1', mobile_phone='777')

with describe('Car wash service') as _:

    @before.each
    def set_up():
        _.notifier = Spy()
        _.car_wash_service = create_car_wash_service(_.notifier, InMemoryJobRepository())

    with context('car wash job'):
        with describe('when the car enters in the car wash'):
            def it_registers_a_job():
                job = _.car_wash_service.enter_in_the_car_wash(car1, customer1)

                assert_that(job.has_customer(customer1), is_(True))
                assert_that(job.service_id, is_not(None))

    with context('customer notification'):
        with describe('when service completed'):
            def it_notifies_the_customer():
                _.car_wash_service.enter_in_the_car_wash(car1, customer1)
                _.car_wash_service.wash_completed('123-XXX.123')

                assert_that(_.notifier.job_completed,
                    called().with_args(_make_car_wash_job_with(car1, customer1)))

    with context('reporting'):
        with describe('when client report requested'):
            def it_shows_all_wash_services_for_that_customer():
                _.car_wash_service.enter_in_the_car_wash(car1, customer2)
                _.car_wash_service.enter_in_the_car_wash(car1, customer1)
                _.car_wash_service.enter_in_the_car_wash(car2, customer1)
                _.car_wash_service.enter_in_the_car_wash(car3, customer1)

                services = _.car_wash_service.services_by_customer(customer1)

                assert_that(services, has_items(_make_car_wash_job_with(car1, customer1),
                                               _make_car_wash_job_with(car2, customer1),
                                               _make_car_wash_job_with(car3, customer1)))
                assert_that(services, not(has_item(_make_car_wash_job_with(car1, customer2))))

    def _make_car_wash_job_with(car, customer):
        return CarWashJob(car, customer)
