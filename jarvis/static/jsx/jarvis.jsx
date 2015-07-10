var Router = ReactRouter;
var { Route, RouteHandler } = Router;

$c = (component) => $(React.findDOMNode(component));

class App extends React.Component {
  render() {
    return (
      <div>
        <nav className="navbar navbar-inverse navbar-static-top">
          <div className="container">
            <div className="row">
              <div className="col-sm-12">
                <div classname="navbar-header">
                  <a className="navbar-brand" href="#">Jarvis</a>
                </div>
              </div>
            </div>
          </div>
        </nav>
        <RouteHandler/>
        <div className="footer">
          <div className="container">
            <div className="row">
              <div className="col-sm-6">
                Made with <i className="glyphicon glyphicon-heart"></i> by Lee Mracek and Max Ovsiankin
              </div>
              <div className="col-sm-6">
                <div className="text-right">
                  Source on <a href="https://github.com/gratimax/jarvis">GitHub</a>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    );
  }
}

class Home extends React.Component {
  render() {
    return (
      <div className="jumbotron">
        <div className="container">
          <h1>Jarvis</h1>
          <p>Jarvis crunches the best De Anza (fall) schedule so that you don't have to.</p>
          <p>
            <a className="btn btn-primary btn-lg" href="#/search-courses">
              Get started »
            </a>
          </p>
        </div>
      </div>
    );
  }
}

class SearchCourses extends React.Component {

  constructor() {
    this.state = {searchQuery: ''};
  }

  handleSearch() {
    this.setState({searchQuery: $c(this.refs.search).val()});
  }

  render() {
    return (
      <div className="container">
        <div className="row">
          <div className="col-sm-12">
            <h1>Search Courses</h1>
            <p>Get started by searching courses.</p>
          </div>
        </div>
        <div className="row">
          <div className="col-sm-3">
            <div className="input-group">
              <input className="form-control" type="text" placeholder="Search..." ref="search"/>
              <span className="input-group-btn">
                <button type="button" className="btn btn-primary" onClick={this.handleSearch.bind(this)}><i className="glyphicon glyphicon-search"></i></button>
              </span>
            </div>
          </div>
          <div className="col-sm-9">
            <SearchResults searchQuery={this.state.searchQuery}/>
          </div>
        </div>
      </div>
    );
  }
}

class SearchResults extends React.Component {

  constructor(props) {
    super(props);
    this.state = {loading: true};
  }

  componentWillReceiveProps(newProps) {
    this.setState({loading: true});
    $.ajax({
      type: 'POST',
      url: '/search',
      data: JSON.stringify({query: newProps.searchQuery}),
      contentType: 'application/json',
      dataType: 'json',
      success: function (data) {
        this.setState({loading: false, results: data});
      }.bind(this)
    });
  }

  render() {
    var output;
    if (this.props.searchQuery == '') {
      output = (
        <ul className="list-group">
          <li className="list-group-item">
            <span className="text-muted">results will appear here...</span>
          </li>
        </ul>
      );
    } else {
      if (this.state.loading) {
        output = <Spinner/>;
      } else {

        var numResults = this.state.results.length;
        output = <ul className="list-item-group">
          <li className="list-group-item text-right">{numResults} {numResults == 1 ? "result" : "results"}</li>
          {
          this.state.results.map(function (result) {
            return <CourseSearchResult course={result}/>;
          })
        }</ul>
      }
    }
    return output;
  }

}

SearchResults.propTypes = { searchQuery: React.PropTypes.String };
SearchResults.defaultProps = { searchQuery: ''};

class CourseSearchResult extends React.Component {

  formatTime(time) {
    return moment({H: time.hours, m: time.minutes}).format('h:mm a');
  }

  meetingTime(time) {
    if (time === "TBA") {
      return time;
    } else {
      return `${this.formatTime(time.start)} - ${this.formatTime(time.end)}`;
    }
  }

  meetingRating(instructor) {
    if (instructor.rating === "unknown") {
      return instructor.rating;
    } else {
      return instructor.rating.score;
    }
  }

  render() {
    return (
      <li className="list-group-item">
        <h4 className="list-group-item-heading">#{this.props.course.crn} <span className="text-muted">({this.props.course.course})</span></h4>
        <p className="list-group-item-text">
          {this.props.course.title}
        </p>
        <table className="table">
          <thead>
            <th>Days</th>
            <th>Location</th>
            <th>Time</th>
            <th>Instructor</th>
            <th>Rating</th>
            <th>Type</th>
          </thead>
          {this.props.course.meetings.map((meeting) => {
            return (
              <tr>
                <td>{meeting.days.map((day) => {
                  return <span>{day}<br/></span>;
                })}</td>
                <td>{meeting.location}</td>
                <td>{this.meetingTime(meeting.time)}</td>
                <td>{meeting.instructor.first_name} {meeting.instructor.last_name}</td>
                <td>{this.meetingRating(meeting.instructor)}</td>
                <td>{meeting.type}</td>
              </tr>
            );
          })}
        </table>
        <div className="row" ref="scheduler">
        </div>
      </li>
    )
  }

}

CourseSearchResult.propTypes = { course: React.PropTypes.Object };
CourseSearchResult.defaultProps = { course: {} };

class Spinner extends React.Component {

  render() {
    return (
      <div className="spinner">
        <div className="rect1"></div>
        <div className="rect2"></div>
        <div className="rect3"></div>
        <div className="rect4"></div>
        <div className="rect5"></div>
      </div>
    )
  }

}

class CourseScheduleVisualization extends React.Component {



}

var routes = (
  <Route handler={App}>
    <Route path="/" handler={Home}/>
    <Route path="search-courses" handler={SearchCourses}/>
  </Route>
);

Router.run(routes, Router.HashLocation, (Root) => {
  React.render(<Root/>, $("#app").get(0));
});
