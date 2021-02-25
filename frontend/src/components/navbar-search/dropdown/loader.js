import React from "react"
import Loader from "limitless/components/loader"

export default function({ message }) {
  return (
    <li className="dropdown-search-loader">
      <Loader />
    </li>
  )
}
