import React from "react"
import Container from "./container"
import Loader from "limitless/components/loader"

export default function(props) {
  return (
    <Container className="posting-loader">
      <Loader />
    </Container>
  )
}
