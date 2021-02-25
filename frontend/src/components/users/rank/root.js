import React from "react"
import PageLead from "limitless/components/page-lead"
import List from "limitless/components/users/rank/list"
import ListLoading from "limitless/components/users/rank/list-loading"
import misago from "limitless/index"
import { hydrate } from "limitless/reducers/users"
import polls from "limitless/services/polls"
import store from "limitless/services/store"
import title from "limitless/services/page-title"

export default class extends React.Component {
  constructor(props) {
    super(props)

    if (misago.has("USERS")) {
      this.initWithPreloadedData(misago.pop("USERS"))
    } else {
      this.initWithoutPreloadedData()
    }

    this.startPolling(props.params.page || 1)
  }

  initWithPreloadedData(data) {
    this.state = Object.assign(data, {
      isLoaded: true
    })
    store.dispatch(hydrate(data.results))
  }

  initWithoutPreloadedData() {
    this.state = {
      isLoaded: false
    }
  }

  startPolling(page) {
    polls.start({
      poll: "rank-users",
      url: misago.get("USERS_API"),
      data: {
        rank: this.props.route.rank.id,
        page: page
      },
      frequency: 90 * 1000,
      update: this.update
    })
  }

  update = data => {
    store.dispatch(hydrate(data.results))

    data.isLoaded = true
    this.setState(data)
  }

  componentDidMount() {
    title.set({
      title: this.props.route.rank.name,
      page: this.props.params.page || null,
      parent: gettext("Users")
    })
  }

  componentWillUnmount() {
    polls.stop("rank-users")
  }

  componentWillReceiveProps(nextProps) {
    if (this.props.params.page !== nextProps.params.page) {
      title.set({
        title: this.props.route.rank.name,
        page: nextProps.params.page || null,
        parent: gettext("Users")
      })

      this.setState({
        isLoaded: false
      })

      polls.stop("rank-users")
      this.startPolling(nextProps.params.page)
    }
  }

  getClassName() {
    if (this.props.route.rank.css_class) {
      return "rank-users-list rank-users-" + this.props.route.rank.css_class
    } else {
      return "rank-users-list"
    }
  }

  getRankDescription() {
    if (this.props.route.rank.description) {
      return (
        <div className="rank-description">
          <PageLead copy={this.props.route.rank.description.html} />
        </div>
      )
    } else {
      return null
    }
  }

  getComponent() {
    if (this.state.isLoaded) {
      if (this.state.count > 0) {
        let baseUrl =
          misago.get("USERS_LIST_URL") + this.props.route.rank.slug + "/"
        return (
          <List baseUrl={baseUrl} users={this.props.users} {...this.state} />
        )
      } else {
        return (
          <p className="lead">
            {gettext("There are no users with this rank at the moment.")}
          </p>
        )
      }
    } else {
      return <ListLoading />
    }
  }

  render() {
    return (
      <div className={this.getClassName()}>
        <div className="container">
          {this.getRankDescription()}
          {this.getComponent()}
        </div>
      </div>
    )
  }
}
