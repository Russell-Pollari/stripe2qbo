import * as React from 'react'
import { useDispatch } from 'react-redux'

import {
    useGetCompanyInfoQuery,
    useDisconnectQBOMutation,
    api,
} from '../services/api'
import ConnectionCard from './ConnectionCard'

const connect = () => {
    fetch('/qbo/oauth2')
        .then((response) => response.json())
        .then((data: string) => {
            location.href = data
        })
}

const QBOConnection = () => {
    const { data: companyInfo, isLoading } = useGetCompanyInfoQuery('')
    const [disconnect] = useDisconnectQBOMutation()
    const dispatch = useDispatch()

    return (
        <ConnectionCard
            title="QuickBooks Online"
            isLoading={isLoading}
            isConnected={!!companyInfo}
            disconnect={() => {
                disconnect('')
                dispatch(api.util.resetApiState())
            }}
        >
            {companyInfo ? (
                <div>
                    {companyInfo.CompanyName} ({companyInfo.Country})
                </div>
            ) : (
                <button
                    className="inline-block hover:bg-slate-100 text-gray-500 font-bold p-2 rounded-full text-sm"
                    onClick={connect}
                >
                    Connect a QBO account
                </button>
            )}
        </ConnectionCard>
    )
}

export default QBOConnection
