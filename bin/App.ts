#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';
import { ServiceStack } from '../lib/ServiceStack';
import { PersistenceStack } from '../lib/PersistenceStack';

const app = new cdk.App();

const persistenceStack = new PersistenceStack(app, 'IHSearchServicePersistenceStack', {
    env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION },
});

new ServiceStack(app, 'IHSearchServiceStack', {
  env: { account: process.env.CDK_DEFAULT_ACCOUNT, region: process.env.CDK_DEFAULT_REGION }
});