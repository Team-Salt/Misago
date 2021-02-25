import React from "react"
import { connect } from "react-redux"
import DropdownToggle from "limitless/components/dropdown-toggle"
import { SideNav, CompactNav } from "limitless/components/options/navs"
import DeleteAccount from "limitless/components/options/delete-account"
import EditDetails from "limitless/components/options/edit-details"
import DownloadData from "limitless/components/options/download-data"
import ChangeForumOptions from "limitless/components/options/forum-options"
import ChangeUsername from "limitless/components/options/change-username/root"
import ChangeSignInCredentials from "limitless/components/options/sign-in-credentials/root"
import WithDropdown from "limitless/components/with-dropdown"
import misago from "limitless/index"

export default class extends WithDropdown {
  render() {
    return (
      <div className="page page-options">
        <div className="page-header-bg">
          <div className="page-header">
            <div className="container">
              <h1>{gettext("Change your options")}</h1>
            </div>
            <div className="page-tabs visible-xs-block visible-sm-block">
              <div className="container">
                <CompactNav
                  className="nav nav-pills"
                  baseUrl={misago.get("USERCP_URL")}
                  options={misago.get("USER_OPTIONS")}
                />
              </div>
            </div>
          </div>
        </div>
        <div className="container">
          <div className="row">
            <div className="col-md-3 hidden-xs hidden-sm">
              <SideNav
                baseUrl={misago.get("USERCP_URL")}
                options={misago.get("USER_OPTIONS")}
              />
            </div>
            <div className="col-md-9">{this.props.children}</div>
          </div>
        </div>
      </div>
    )
  }
}

export function select(store) {
  return {
    tick: store.tick.tick,
    user: store.auth.user,
    "username-history": store["username-history"]
  }
}

export function paths() {
  const SSO_ENABLED = misago.get("SETTINGS").enable_sso

  const paths = [
    {
      path: misago.get("USERCP_URL") + "forum-options/",
      component: connect(select)(ChangeForumOptions)
    },
    {
      path: misago.get("USERCP_URL") + "edit-details/",
      component: connect(select)(EditDetails)
    }
  ]

  if (!SSO_ENABLED) {
    paths.push({
      path: misago.get("USERCP_URL") + "change-username/",
      component: connect(select)(ChangeUsername)
    })
    paths.push({
      path: misago.get("USERCP_URL") + "sign-in-credentials/",
      component: connect(select)(ChangeSignInCredentials)
    })
  }

  if (misago.get("ENABLE_DOWNLOAD_OWN_DATA")) {
    paths.push({
      path: misago.get("USERCP_URL") + "download-data/",
      component: connect(select)(DownloadData)
    })
  }

  if (!SSO_ENABLED && misago.get("ENABLE_DELETE_OWN_ACCOUNT")) {
    paths.push({
      path: misago.get("USERCP_URL") + "delete-account/",
      component: connect(select)(DeleteAccount)
    })
  }

  return paths
}
