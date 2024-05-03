# Scheduled In-Queue Callbacks

This is a proof-of-concept prototype to implement `scheduled in-queue callbacks` in Amazon Connect.  Note that it should **not** be considered a production-ready implementation, just a demonstration of what can be done.

## Problem Definition

### Callbacks

For the purpose of this prototype, a `callback` is determined to be an outbound call to a customer which has been expressly requested by the customer at a particular point in time (approximately). This is different from any form of "cold-call" or sales contacts.

We group these into two categories:
* `queued` or `in-queue` callbacks which have been requested "as soon as possible".  These are offered out-of-the-box in Amazon Connect, and explained in more detail below.
* `scheduled` callbacks which have been requested for a particular point in time, e.g. "please call me back at 5pm tomorrow"

### Start Outbound Voice Contact

Presently, there is only one method to programmatically dial an external phone number from Amazon Connect: the [StartOutboundVoiceContact](https://docs.aws.amazon.com/connect/latest/APIReference/API_StartOutboundVoiceContact.html) API.  It works as follows:

![Start Outbound Voide Contact](docs/sovc.png)

Unfortunately it has one large problem: because it will only connect an agent *after* the customer has already answered, there will be a noticable delay between the two. In this time:
* The customer may hang up before the agent can explain the reason for the call
* The call may hit a voicemail which is shorter than the delay, resulting in the agent leaving an awkward message for the customer

This behaviour is likely intentional as it fits a more normal "outbound" paradigm, where the expectation is that relatively few calls will be answered, and the benefit of reduced agent handle time outweighs the cost to customer experience.

But considering that these scheduled callbacks have been explicitly requested our requirements are different: we'd prefer to offer a better experience to the customer, even if it means holding up the agent while we dial.

### In-Queue Callbacks

There is an [in-built form of callback](https://docs.aws.amazon.com/connect/latest/adminguide/setup-queued-cb.html) offered by Amazon Connect, which we refer to as `queued` or `in-queue` callbacks.  Unlike scheduled callbacks these are designed to be immediate, and specifically offered to customers to avoid waiting in long queues.

![In-Queue Callbacks](docs/iqc.png)

As these callbacks are inserted into queues they behave like any reqular inbound call, except that the customer is not currently on the line.  Instead, it waits in the queue until an agent is ready to accept it, and only after they've done so does it dial the outbound number.  As such the agent is available to greet the customer immediately after they answer.

Unfortunately, there is no way to programmatically trigger the creation of such a callback: it can only be done as part of an inbound contact flow, triggered from a phone call.

## Design Overview

### Assumptions

This prototype assumes that the user already has some mechanism to:
* Receive a request for a scheduled callback
* Store the callback details
* Automatically trigger an event when the time expires

The prototype represents the continuation of the third step, i.e. when the event fires it will create a scheduled "in-queue" callback.

### Detail

In general, the prototype creates an *outbound* call to an *inbound* number, but provides a general contact flow for the outbound side of the call in which we create the in-queue callback. Specifically:

![Scheduled In-Queue Callbacks](docs/siqc.png)

* The `start_outbound.py` script, designed to replicate the behaviour that would be implemented on the expiration event, starts an outbound voice contact with the following parameters:
  * `Destination` - an inbound phone number in the connect instance, which points to the `CallbackInbound` flow
  * `ContactFlow` - the `CallbackOutbound` flow.
  * A number of user-defined attributes, including:
    * `CallbackNumber` - the customer's phone number, which is the target of the callback
    * `CallerId` - \[optional\] the instance phone number that will appear as the "from" number to the customer
* Both sides of the call run simultaneously:
  * `CallbackInbound`
    * Simply transfer to a queue that no agent is servicing
    * Wait here until the "agent" disconnects (see below)
  * `CallbackOutbound`
    * Sets the outbound number, as provided in the attributes
    * Creates an in-queue callback and transfers to the callback queue
    * Terminates the current call before it's offered to an agent, which also ends the inbound side
* When an agent is ready to service the queue:
  * The callback is dequeued to the agent
  * The `CallbackAgentWhisper` flow runs, providing the agent a prompt about the callback
  * The `CallbackOutboundWhisper` flow runs, setting the outbound caller id
  * The customer phone number is dialled
* When the customer answers, the two-way call is finally initiated

Note that the last two sections are consistent with regular callback behaviour, but they've been noted here to show that attributes provided all the way back at the start (in the call to `StartOutboundVoiceContact`) automatically propogate through to them. This allows us to do things like setting the outbound caller id without needing to call out for details via a lambda.

### Limitations

The main problem with this prototype is the "useless" outbound call which just sits in the inbound queue until the callback has been created.  Unfortunately, this is necessary - the outbound contact flow won't run until the inbound has been answered (which is exactly the same problem that led to the creation of this prototype in the first place).

In general, this inbound call is harmless, but note the following:

* It will count as a phone call for billing and expenses.  Fortunately it should only last as long as it takes for the outbound flow to create the callback, but note that AWS billing may charge for a minimum duration.
* Any genuine calls to the same number will also go to the dummy queue, and therefore never be serviced.  This is why it's referred to here as the "private" number, indicating it should never be advertised. A potential robustiness enhancement could involve adding a custom check to ensure the "customer" number is the one from our instance.
* It will appear in reporting and logs, and could be confused with real inbound calls.

Additionally, we want to ensure that agents are never servicing the dummy queue: if they do it could be a bad experience, especially if they somehow managed to answer and disconnect before the callback was able to be created.

Finally, note that this prototype only puts the callback into the queue: the time that the callback will be made is dependant on when an agent is available.  This has a number of potential advantages, such as blending with regular inbound calls based on priority, but a production-ready solution should have some way to confirm that the actual callback has been completed.

## Running the Demo

**Note:** this prototype is provided for demonstration purposes only, please run it at your own risk.  See the [license](./LICENSE) for further details.

### Requirements

* `python3`, with `pipenv` globally installed. The prototype was written for version `3.10`
* An AWS account with the following:
  * `Connect Instance` with:
    * At least one `agent user`
    * Two dedicated `phone numbers`
* An `IAM user/role`:
  * With permission to perform basic tasks
  * Able to run locally, i.e. with local credentials

### Steps

The following scripts are designed to be run from the `src` directory.

#### Environment File

First, fill in the [.env](./.env) file in the base directory with the variables relevant to your setup:
* `InstanceAlias` - the alias of your Connect instance
* `PrivateNumber` - the number that you will call to trigger the callback
* `PublicNumber` - the number to use as the "outbound source"
* `AgentUsername` - the username of the agent that you will be testing with
* `CustomerNumber` - the customer number to dial.  The prototype will actively dial
* `CallerId` - \[optional] the instance phone number that will appear as the "from" number to the customer. If blank, will default to the one on the queue

Phone numbers should be in E.164 format - pay particular attention to ensuring the `PrivateNumber` and `CustomerNumber` are correct as these will be actively dialled out to.

Note also that having two separate instance numbers is necessary as sending an outbound request with the Source and Destination match will quietly fail.

#### Setup

Run the full setup with `python3 -m deploy.setup`.  This will:
1. Deploy the stacks
1. Assign the phone number to the contact flow
1. Assign the agent to the routing profile

You can also run `python3 -m deploy.deploy` to just deploy the stacks.

#### Teardown

When you want to delete the stacks, you'll first need to unassign the user and phone number.  You can do that with `python3 -m deploy.teardown`.  Note that this won't delete the stacks, you'll have to do that manually.

### Developing

### Requirements

These are mostly the same as those needed for testing, though you'll also `graphviz` if you want to run the documentation generator.

### Steps

Run `init.sh` to install dependencies and the pre-commit hook.

If you want to make changes to the contact flows, do the following:
1. Ensure the flows have been deployed (i.e. run the `deploy` or `setup` scripts)
1. Make the changes manually in the Connect console
1. Run the `export` script to download the contact flows to your machine: `python3 -m export.export`
1. Run the `templatise` script to translate the downloaded flows.  This replaces hardcoded ARNs with jinja2 template variables, which are rendered to the correct ARNs at deploy time: `python3 -m export.templatise`

## TODO

* Add callback notes to default agent whisper
* Add unit tests
* Ruff look at unused imports or args