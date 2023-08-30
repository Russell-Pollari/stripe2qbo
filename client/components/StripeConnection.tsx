import * as React from 'react'
import { useDispatch } from 'react-redux'

import ConnectionCard from './ConnectionCard'
import {
    useGetStripeInfoQuery,
    useDisconnectStripeMutation,
    api,
} from '../services/api'

const connect = () => {
    fetch('/stripe/oauth2')
        .then((response) => response.json())
        .then((data: string) => {
            location.href = data
        })
}

const StripeConnection = () => {
    const { data: stripeInfo, isLoading } = useGetStripeInfoQuery('')
    const [disconnect] = useDisconnectStripeMutation()
    const dispatch = useDispatch()

    return (
        <ConnectionCard
            isConnected={!!stripeInfo}
            title="Stripe account"
            isLoading={isLoading}
            disconnect={() => {
                disconnect('')
                dispatch(api.util.resetApiState())
            }}
        >
            {stripeInfo ? (
                <span>
                    {stripeInfo.business_profile.name || stripeInfo.id} (
                    {stripeInfo.country})
                </span>
            ) : (
                <button
                    className="inline-block hover:bg-slate-100 text-gray-500 font-bold p-2 rounded-full text-sm"
                    onClick={connect}
                >
                    Connect a Stripe account
                </button>
            )}
        </ConnectionCard>
    )
}

export default StripeConnection
