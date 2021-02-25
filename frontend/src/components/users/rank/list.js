import React from "react"
import Pager from "limitless/components/users/rank/pager"
import UsersList from "limitless/components/users-list"

export default function(props) {
  return (
    <div>
      <UsersList
        cols={4}
        isReady={true}
        showStatus={true}
        users={props.users}
      />
      <Pager {...props} />
    </div>
  )
}
