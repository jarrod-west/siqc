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

Considering that these scheduled callbacks are actually requested by the customer, though, our requirements are different: we'd prefer to offer a better experience to the customer, even if it means holding up the agent while we dial.

### In-Queue Callbacks

There is an [in-built form of callback](https://docs.aws.amazon.com/connect/latest/adminguide/setup-queued-cb.html) offered by Amazon Connect, which we refer to as `queued` or `in-queue` callbacks.  Unlike scheduled callbacks these are designed to be immediate, and specifically offered to customers to avoid waiting in long queues.

![In-Queue Callbacks](docs/iqc.png)

As these callbacks sit in a queue, they behave like any reqular inbound call, except that the customer is not currently on the line.  Instead, it waits in the queue until an agent is ready to accept it, and only after they've done so does it dial the outbound number.  As such the agent is available to greet the customer immediately after they answer.

Unfortunately, there is no way to programmatically trigger the creation of such a callback: it can only be done as part of an inbound contact flow, triggered from a phone call.

## Design Overview
![Scheduled In-Queue Callbacks](docs/siqc.png)

### Assumptions

This prototype assumes that you already have some mechanism to:
* Receive a request for a scheduled callback
* Store the callback details
* Automatically trigger an event when the time expires

The prototype represents the continuation of the third step, i.e. when the event fires it will create a scheduled "in-queue" callback.

### Detail

In general, the prototype creates an *outbound* call to an *inbound* number, and uses that inbound contact flow to create the in-queue callback.  Specifically:

* A start-script, designed to be triggered from the expiration event, does the following:
  * Pushes the relevant callback details to an SQS queue
  * Starts an outbound voice contact:
    * `Destination` = an inbound phone number in the connect instance, which points to the `CallbackInbound` flow
    * `ContactFlow` = the `CallbackOutbound` flow.
* Both sides of the call run simultaneously:
  * `CallbackOutbound`
    * Simply transfer to a queue that no agent is servicing
    * Wait here until the "customer" disconnects (see below)
  * `CallbackInbound`
    * Calls the lambda to pop the callback details from an SQS queue and return them
    * Sets the outbound number, as provided in the callback details
    * Creates an in-queue callback and transfers to the callback queue
    * Terminates the current call, which also ends the outbound side

From here, the behaviour is the same as an in-queue callback, i.e. an agent servicing the callback queue will pick it up and only then will the system dial the customer.

### Limitations

`TODO:` 

## Running the Demo

### Requirements

* `python3`, with `pipenv` globally installed. The prototype was written for version `3.10`
* `docker` for the package generator
* An AWS account with the following:
  * `Connect Instance` with:
    * At least one `agent user`
    * Two dedicated `phone numbers`
  * `S3 bucket` - to store the lambda code
* An `IAM user/role`:
  * With permission to perform basic tasks
  * Able to run locally, i.e. with local credentials

### Steps

`TODO:` Liability disclaimer

The following scripts are designed to be run from the `src` directory.

#### Environment File

First, fill in the [.env](./.env) file in the base directory with the variables relevant to your setup:
* `InstanceAlias` - the alias of your Connect instance
* `PrivateNumber` - the number that you will call to trigger the callback
* `PublicNumber` - the number to use as the "outbound source"
* `AgentUsername` - the username of the agent that you will be testing with
* `DeploymentBucket` - the S3 bucket to use for the lambda deployment
* `DeploymentPath` - the "directory" in the S3 bucket where the lambda will be deployed

#### Setup

Run the full setup with `python3 -m deploy.setup`.  This will:
1. build the lambda package
1. deploy the stacks
1. assign the phone number to the contact flow
1. assign the agent to the routing profile

You can also run `python3 -m deploy.deploy` to just build the package and deploy the stacks.

#### Teardown

When you want to delete the stacks, you'll first need to unassign the user and phone number.  You can do that with `python3 -m deploy.teardown`.  Note that this won't delete the stacks, you'll have to do that manually.

### Developing

### Requirements

These are the mostly the same as those needed for testing, though you'll also `graphviz` if you want to run the documentation generator

### Steps

Run `init.sh` to install dependencies and the pre-commit hook.

If you want to make changes to the contact flows, do the following:
1. Ensure the flows have been deployed (i.e. run the `deploy` or `setup` scripts)
1. Make the changes manually in the Connect console
1. Run the `export` script to download the contact flows to your machine: `python3 -m export.export`
1. Run the `templatise` script to translate the downloaded flows.  This replaces hardcoded ARNs with jinja2 template variables, which are rendered to the correct ARNs at deploy time: `python3 -m export.templatise`

## TODO

* Update for default flow:
  * Only need one phone number now?

* Finalise "start outbound" script
* Consider deleting stacks in teardown script
* Add callback notes to default agent whisper
* Use docstrings
* Add unit tests