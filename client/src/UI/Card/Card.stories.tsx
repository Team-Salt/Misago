import React from "react"
import { RootContainer } from "../Storybook"
import { ButtonPrimary } from "../Button"
import {
  Card,
  CardBanner,
  CardBlankslate,
  CardBody,
  CardColorBand,
  CardError,
  CardFooter,
  CardHeader,
  CardList,
  CardListItem,
  CardLoader,
} from "."

export default {
  title: "UI/Card",
}

export const Basic = () => {
  return (
    <RootContainer padding>
      <Card>
        <CardBody>Lorem ipsum dolor met</CardBody>
      </Card>
    </RootContainer>
  )
}

export const HeaderAndFooter = () => {
  return (
    <RootContainer padding>
      <Card>
        <CardHeader title="Hello world" />
        <CardBody>Lorem ipsum dolor met</CardBody>
        <CardFooter>Do something</CardFooter>
      </Card>
    </RootContainer>
  )
}

export const WithBanner = () => {
  return (
    <RootContainer padding>
      <Card>
        <CardBanner
          align="center"
          background="#2c3e50"
          height={100}
          url="http://lorempixel.com/1280/200/"
        />
        <CardBanner
          align="center"
          background="#2c3e50"
          height={100}
          url="http://lorempixel.com/1536/200/"
          mobile
        />
        <CardBody>Lorem ipsum dolor met</CardBody>
      </Card>
    </RootContainer>
  )
}

export const WithColorBand = () => {
  return (
    <RootContainer padding>
      <Card>
        <CardColorBand color="#ff5630" />
        <CardBody>Lorem ipsum dolor met</CardBody>
      </Card>
    </RootContainer>
  )
}

export const WithColorBandBanner = () => {
  return (
    <RootContainer padding>
      <Card>
        <CardColorBand color="#ff5630" />
        <CardBanner
          align="center"
          background="#2c3e50"
          height={100}
          url="http://lorempixel.com/1280/200/"
        />
        <CardBanner
          align="center"
          background="#2c3e50"
          height={100}
          url="http://lorempixel.com/1536/200/"
          mobile
        />
        <CardBody>Lorem ipsum dolor met</CardBody>
      </Card>
    </RootContainer>
  )
}

export const List = () => {
  return (
    <RootContainer padding>
      <Card>
        <CardList>
          <CardListItem>
            Nam rhoncus ipsum non neque dapibus, sit amet condimentum est
            faucibus.
          </CardListItem>
          <CardListItem>
            Sed porttitor semper massa, sit amet ultrices velit lobortis ac.
          </CardListItem>
        </CardList>
      </Card>
    </RootContainer>
  )
}

export const ListWithLoader = () => {
  return (
    <RootContainer padding>
      <Card>
        <CardList>
          <CardListItem>
            Nam rhoncus ipsum non neque dapibus, sit amet condimentum est
            faucibus.
          </CardListItem>
          <CardListItem>
            Sed porttitor semper massa, sit amet ultrices velit lobortis ac.
          </CardListItem>
        </CardList>
        <CardLoader />
      </Card>
    </RootContainer>
  )
}

export const Loader = () => {
  return (
    <RootContainer padding>
      <Card>
        <CardLoader />
      </Card>
    </RootContainer>
  )
}

export const Blankslate = () => {
  return (
    <RootContainer padding>
      <Card>
        <CardBlankslate header="JohnDoe has no threads." />
      </Card>
    </RootContainer>
  )
}

export const BlankslateWithMessage = () => {
  return (
    <RootContainer padding>
      <Card>
        <CardBlankslate
          header="There are no threads in this category."
          message="Why not start one yourself?"
        />
      </Card>
    </RootContainer>
  )
}

export const BlankslateWithMessageAction = () => {
  return (
    <RootContainer padding>
      <Card>
        <CardBlankslate
          header="There are no threads in this category."
          message="Why not start one yourself?"
          actions={<ButtonPrimary text={"Start thread"} onClick={() => {}} />}
        />
      </Card>
    </RootContainer>
  )
}

export const BlankslateWithAction = () => {
  return (
    <RootContainer padding>
      <Card>
        <CardBlankslate
          header="There are no threads in this category."
          actions={<ButtonPrimary text={"Start thread"} onClick={() => {}} />}
        />
      </Card>
    </RootContainer>
  )
}

export const Error = () => (
  <RootContainer padding>
    <Card>
      <CardError header="This content is not available at the moment" />
    </Card>
  </RootContainer>
)

export const ErrorWithMessage = () => (
  <RootContainer padding>
    <Card>
      <CardError
        header="This content is not available."
        message={
          "It may have been moved or deleted, or you are missing permission to see it."
        }
      />
    </Card>
  </RootContainer>
)