import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Progress } from '@/components/ui/progress.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Alert, AlertDescription } from '@/components/ui/alert.jsx'
import { 
  Search, 
  Globe, 
  Smartphone, 
  Zap, 
  CheckCircle, 
  XCircle, 
  AlertTriangle,
  BarChart3,
  Shield,
  Clock,
  TrendingUp
} from 'lucide-react'
import './App.css'

const API_BASE_URL = 'http://localhost:5001/api'

function App() {
  const [url, setUrl] = useState('')
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResults, setAnalysisResults] = useState(null)
  const [error, setError] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [showApiKeyInput, setShowApiKeyInput] = useState(true)
  const [engines, setEngines] = useState(['technical', 'performance', 'seo', 'mobile'])

  const validateUrl = (url) => {
    try {
      new URL(url)
      return true
    } catch {
      return false
    }
  }

  const handleAnalyze = async () => {
    if (!url) {
      setError('Please enter a URL to analyze')
      return
    }

    if (!validateUrl(url)) {
      setError('Please enter a valid URL (including http:// or https://)')
      return
    }

    if (!apiKey) {
      setError('Please enter your API key')
      return
    }

    setError('')
    setIsAnalyzing(true)
    setAnalysisResults(null)

    try {
      const response = await fetch(`${API_BASE_URL}/analyze/url`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${apiKey}`
        },
        body: JSON.stringify({
          url: url,
          engines: engines,
          priority: 'normal'
        })
      })

      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || `HTTP error! status: ${response.status}`)
      }

      // Get detailed results
      const resultsResponse = await fetch(`${API_BASE_URL}/analyze/results/${data.analysis_id}`, {
        headers: {
          'Authorization': `Bearer ${apiKey}`
        }
      })

      const resultsData = await resultsResponse.json()

      if (resultsResponse.ok) {
        setAnalysisResults(resultsData)
      } else {
        // If results not ready, show basic completion info
        setAnalysisResults({
          analysis: { url: url, status: 'completed' },
          summary: { overall_score: 0 },
          results: {},
          recommendations: []
        })
      }

    } catch (err) {
      setError(err.message)
    } finally {
      setIsAnalyzing(false)
    }
  }

  const getScoreColor = (score) => {
    if (score >= 80) return 'text-green-600'
    if (score >= 60) return 'text-yellow-600'
    return 'text-red-600'
  }

  const getScoreBadgeVariant = (score) => {
    if (score >= 80) return 'default'
    if (score >= 60) return 'secondary'
    return 'destructive'
  }

  const getPriorityIcon = (priority) => {
    switch (priority) {
      case 'high': return <XCircle className="h-4 w-4 text-red-500" />
      case 'medium': return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case 'low': return <CheckCircle className="h-4 w-4 text-green-500" />
      default: return <CheckCircle className="h-4 w-4 text-gray-500" />
    }
  }

  const getEngineIcon = (engine) => {
    switch (engine) {
      case 'technical': return <Shield className="h-5 w-5" />
      case 'performance': return <Zap className="h-5 w-5" />
      case 'seo': return <TrendingUp className="h-5 w-5" />
      case 'mobile': return <Smartphone className="h-5 w-5" />
      default: return <BarChart3 className="h-5 w-5" />
    }
  }

  const getEngineTitle = (engine) => {
    switch (engine) {
      case 'technical': return 'Technical Accessibility'
      case 'performance': return 'Core Web Vitals'
      case 'seo': return 'SEO Optimization'
      case 'mobile': return 'Mobile-Friendliness'
      default: return engine
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 dark:from-gray-900 dark:to-gray-800">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 dark:text-white mb-4">
            URL Scanner
          </h1>
          <p className="text-xl text-gray-600 dark:text-gray-300 mb-2">
            Analyze your website for Google Search Console best practices
          </p>
          <p className="text-sm text-gray-500 dark:text-gray-400">
            Check technical accessibility, Core Web Vitals, SEO optimization, and mobile-friendliness
          </p>
        </div>

        {/* API Key Input */}
        {showApiKeyInput && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Shield className="h-5 w-5" />
                API Authentication
              </CardTitle>
              <CardDescription>
                Enter your API key to access the URL scanner service
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2">
                <Input
                  type="password"
                  placeholder="Enter your API key..."
                  value={apiKey}
                  onChange={(e) => setApiKey(e.target.value)}
                  className="flex-1"
                />
                <Button 
                  onClick={() => setShowApiKeyInput(false)}
                  disabled={!apiKey}
                >
                  Continue
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* URL Input */}
        {!showApiKeyInput && (
          <Card className="mb-6">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Globe className="h-5 w-5" />
                URL Analysis
              </CardTitle>
              <CardDescription>
                Enter the URL you want to analyze for Google Search Console compliance
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex gap-2 mb-4">
                <Input
                  type="url"
                  placeholder="https://example.com"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  className="flex-1"
                  disabled={isAnalyzing}
                />
                <Button 
                  onClick={handleAnalyze}
                  disabled={isAnalyzing || !url}
                  className="min-w-[120px]"
                >
                  {isAnalyzing ? (
                    <>
                      <Clock className="h-4 w-4 mr-2 animate-spin" />
                      Analyzing...
                    </>
                  ) : (
                    <>
                      <Search className="h-4 w-4 mr-2" />
                      Analyze
                    </>
                  )}
                </Button>
              </div>

              {/* Engine Selection */}
              <div className="flex flex-wrap gap-2">
                <span className="text-sm text-gray-600 dark:text-gray-400 mr-2">Analysis engines:</span>
                {['technical', 'performance', 'seo', 'mobile'].map((engine) => (
                  <Badge 
                    key={engine}
                    variant={engines.includes(engine) ? 'default' : 'outline'}
                    className="cursor-pointer"
                    onClick={() => {
                      if (engines.includes(engine)) {
                        setEngines(engines.filter(e => e !== engine))
                      } else {
                        setEngines([...engines, engine])
                      }
                    }}
                  >
                    {getEngineIcon(engine)}
                    <span className="ml-1">{getEngineTitle(engine)}</span>
                  </Badge>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {/* Error Display */}
        {error && (
          <Alert className="mb-6 border-red-200 bg-red-50 dark:border-red-800 dark:bg-red-900/20">
            <XCircle className="h-4 w-4" />
            <AlertDescription className="text-red-800 dark:text-red-200">
              {error}
            </AlertDescription>
          </Alert>
        )}

        {/* Analysis Progress */}
        {isAnalyzing && (
          <Card className="mb-6">
            <CardContent className="pt-6">
              <div className="text-center">
                <div className="animate-pulse mb-4">
                  <BarChart3 className="h-12 w-12 mx-auto text-blue-500" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Analyzing your website...</h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Running comprehensive analysis across all selected engines
                </p>
                <Progress value={75} className="w-full max-w-md mx-auto" />
              </div>
            </CardContent>
          </Card>
        )}

        {/* Results Display */}
        {analysisResults && !isAnalyzing && (
          <div className="space-y-6">
            {/* Overall Score */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center justify-between">
                  <span>Analysis Results</span>
                  <Badge variant={getScoreBadgeVariant(analysisResults.summary?.overall_score || 0)}>
                    Score: {Math.round(analysisResults.summary?.overall_score || 0)}/100
                  </Badge>
                </CardTitle>
                <CardDescription>
                  Analyzed: {analysisResults.analysis?.url}
                </CardDescription>
              </CardHeader>
            </Card>

            {/* Detailed Results */}
            <Tabs defaultValue="overview" className="w-full">
              <TabsList className="grid w-full grid-cols-5">
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="technical">Technical</TabsTrigger>
                <TabsTrigger value="performance">Performance</TabsTrigger>
                <TabsTrigger value="seo">SEO</TabsTrigger>
                <TabsTrigger value="mobile">Mobile</TabsTrigger>
              </TabsList>

              <TabsContent value="overview" className="space-y-4">
                {/* Engine Scores */}
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {Object.entries(analysisResults.results || {}).map(([engine, result]) => (
                    <Card key={engine}>
                      <CardContent className="pt-6">
                        <div className="flex items-center justify-between mb-2">
                          {getEngineIcon(engine)}
                          <Badge variant={getScoreBadgeVariant(result.score || 0)}>
                            {result.score || 0}
                          </Badge>
                        </div>
                        <h3 className="font-semibold">{getEngineTitle(engine)}</h3>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {result.recommendations?.length || 0} recommendations
                        </p>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                {/* Top Recommendations */}
                <Card>
                  <CardHeader>
                    <CardTitle>Priority Recommendations</CardTitle>
                    <CardDescription>
                      Top issues that need immediate attention
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {analysisResults.recommendations?.slice(0, 5).map((rec, index) => (
                        <div key={index} className="flex items-start gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-800">
                          {getPriorityIcon(rec.priority)}
                          <div className="flex-1">
                            <h4 className="font-medium">{rec.issue}</h4>
                            <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                              {rec.recommendation}
                            </p>
                            <Badge variant="outline" className="mt-2">
                              {rec.category}
                            </Badge>
                          </div>
                        </div>
                      )) || (
                        <p className="text-gray-500 dark:text-gray-400 text-center py-4">
                          No recommendations available
                        </p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>

              {/* Individual Engine Tabs */}
              {['technical', 'performance', 'seo', 'mobile'].map((engine) => (
                <TabsContent key={engine} value={engine}>
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        {getEngineIcon(engine)}
                        {getEngineTitle(engine)} Analysis
                      </CardTitle>
                      <CardDescription>
                        Detailed analysis results and recommendations
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      {analysisResults.results?.[engine] ? (
                        <div className="space-y-4">
                          <div className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
                            <span className="font-medium">Overall Score</span>
                            <Badge variant={getScoreBadgeVariant(analysisResults.results[engine].score || 0)}>
                              {analysisResults.results[engine].score || 0}/100
                            </Badge>
                          </div>
                          
                          <div>
                            <h4 className="font-medium mb-3">Recommendations</h4>
                            <div className="space-y-2">
                              {analysisResults.results[engine].recommendations?.map((rec, index) => (
                                <div key={index} className="flex items-start gap-3 p-3 border rounded-lg">
                                  {getPriorityIcon(rec.priority)}
                                  <div className="flex-1">
                                    <h5 className="font-medium">{rec.issue}</h5>
                                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                                      {rec.recommendation}
                                    </p>
                                    {rec.impact && (
                                      <p className="text-xs text-gray-500 dark:text-gray-500 mt-2">
                                        Impact: {rec.impact}
                                      </p>
                                    )}
                                  </div>
                                </div>
                              )) || (
                                <p className="text-gray-500 dark:text-gray-400 text-center py-4">
                                  No specific recommendations for this engine
                                </p>
                              )}
                            </div>
                          </div>
                        </div>
                      ) : (
                        <p className="text-gray-500 dark:text-gray-400 text-center py-8">
                          No data available for {getEngineTitle(engine)} analysis
                        </p>
                      )}
                    </CardContent>
                  </Card>
                </TabsContent>
              ))}
            </Tabs>
          </div>
        )}

        {/* Footer */}
        <div className="text-center mt-12 pt-8 border-t border-gray-200 dark:border-gray-700">
          <p className="text-sm text-gray-500 dark:text-gray-400">
            URL Scanner - Powered by comprehensive Google Search Console best practices analysis
          </p>
        </div>
      </div>
    </div>
  )
}

export default App

