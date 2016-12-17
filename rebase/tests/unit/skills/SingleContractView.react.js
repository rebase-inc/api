import React, { Component, PropTypes } from 'react';
import ReactDOM from 'react-dom';

import ContractHeader from './ContractHeader.react';
import ContractStatusHeader from './ContractStatusHeader.react';
import CommentBox from './CommentBox.react';
import ContractDetails from './ContractDetails.react';
import Comment from './Comment.react';
import { humanReadableDate } from '../utils/date';
import { getContractTicket, getContractWork, getContractComments } from '../utils/getters';
import { FAIL, REVIEW, RESOLVE } from '../constants/MediationAnswers';
import { DISCUSSION, WAITING_FOR_DEV, WAITING_FOR_CLIENT } from '../constants/MediationStates';
import { BLOCKED, IN_REVIEW, IN_PROGRESS, IN_MEDIATION, WAIT_FOR_RATING } from '../constants/WorkStates';

export default class SingleContractView extends Component {
    static propTypes = {
        user: PropTypes.object.isRequired,
        role: PropTypes.object.isRequired,
        contract: PropTypes.object.isRequired,
        contracts: PropTypes.array.isRequired,
        actions: PropTypes.object.isRequired,
    }

    constructor(props, context) {
        super(props, context);
    }

    // There has got to be a better way to do this...
    makeCommentButtons(role, contractId, contracts, work, actions) {
        switch (work.state) {
            case IN_PROGRESS:
                return role.type == 'manager' ? null : [
                    <button data-okay onClick={actions.submitWork.bind(null, work)} key='submit'>Submit Work</button>,
                    <button data-alert onClick={actions.markWorkBlocked.bind(null, work)} data-alert key='blocked'>Mark Blocked</button>
                ];
                break;
            case WAIT_FOR_RATING:
            case IN_REVIEW:
                return role.type == 'contractor' ? null : [
                    <button data-okay onClick={actions.acceptWork.bind(null, work, contractId, contracts)} key='accept'>Accept Work</button>,
                    <button data-warning onClick={actions.disputeWork.bind(null, work)} data-alert key='dispute'>Dispute</button>
                ];
                break;
            case BLOCKED:
                return <button data-alert onClick={actions.markWorkUnblocked.bind(null, work)} key='unblockWork'>Unblock</button>;
                break;
            case IN_MEDIATION:
                const mediation_index = work.mediations.length - 1;
                const mediation = work.mediations[mediation_index];
                let waitingForResponse = (mediation.state == DISCUSSION);
                waitingForResponse = waitingForResponse || (role.type == 'contractor' && mediation.state == WAITING_FOR_DEV);
                waitingForResponse = waitingForResponse || (role.type == 'manager' && mediation.state == WAITING_FOR_CLIENT);
                return !waitingForResponse ? null : [
                    <button data-okay onClick={actions.sendMediationAnswer.bind(null, role.type, contractId, mediation_index, mediation, RESOLVE)} key='resolve'>{'Fix issues'}</button>,
                    <button data-alert onClick={actions.sendMediationAnswer.bind(null, role.type, contractId, mediation_index, mediation, REVIEW)} key='review'>{'Ignore issues'}</button>,
                    <button data-warning onClick={actions.sendMediationAnswer.bind(null, role.type, contractId, mediation_index, mediation, FAIL)} key='fail'>{'Give Up'}</button>
                ];
                break;
            default:
                console.warn('Invalid work state: ', work.state);
                return null;
        }
    }

    render() {
        const { contract, contracts, user, role, actions } = this.props;
        if (!contract) { return <div className='singleView'> { 'No Contract Selected' } </div>; }
        const ticket = getContractTicket(contract);
        const work = getContractWork(contract);
        const submitComment = actions.commentOnContract.bind(null, user, contract);
        return (
            <div className='singleView'>
                <ContractHeader actions={actions} contract={contract} role={role} />
                <div className='content'>
                    <div className='scrollable'>
                        { getContractComments(contract).map(comment => <Comment comment={comment} key={comment.id} /> ) }
                        <CommentBox submit={submitComment}>
                            { this.makeCommentButtons(role, contract.id, contracts, work, actions) }
                        </CommentBox>
                    </div>
                    <ContractDetails contract={contract} />
                </div>
            </div>
        );
    }
}

