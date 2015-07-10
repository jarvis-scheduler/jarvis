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
          <div className="col-sm-4">
            <div className="input-group">
              <input className="form-control" type="text" placeholder="Search..." ref="search"/>
              <span className="input-group-btn">
                <button type="button" className="btn btn-primary" onClick={this.handleSearch.bind(this)}><i className="glyphicon glyphicon-search"></i></button>
              </span>
            </div>
          </div>
          <div className="col-sm-8">
            <SearchResults searchQuery={this.state.searchQuery}/>
          </div>
        </div>
      </div>
    );
  }
}

class SearchResults extends React.Component {

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
      output = <div>{this.props.searchQuery}</div>
    }
    return output;
  }

}

SearchResults.propTypes = { searchQuery: React.PropTypes.String };
SearchResults.defaultProps = { searchQuery: ''};

var routes = (
  <Route handler={App}>
    <Route path="/" handler={Home}/>
    <Route path="search-courses" handler={SearchCourses}/>
  </Route>
);

Router.run(routes, Router.HashLocation, (Root) => {
  React.render(<Root/>, document.body);
});
