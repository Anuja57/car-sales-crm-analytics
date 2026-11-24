import axios from 'axios'

export async function analyzeFiles(leadsFile, callsFile, tdFile) {
  const form = new FormData()
  form.append('leads_file', leadsFile)
  form.append('calls_file', callsFile)
  form.append('td_file',    tdFile)
  const { data } = await axios.post('/api/analyze', form, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function getAgentInsights(metrics, tierDist, avgScore, apiKey) {
  const { data } = await axios.post('/api/insights/agent', {
    api_key:   apiKey,
    metrics,
    tier_dist: tierDist,
    avg_score: avgScore,
  })
  return data.insight
}

export async function getConnectivityInsights(segments, avgCalls, avgCbRate, leadTypeDist, apiKey) {
  const { data } = await axios.post('/api/insights/connectivity', {
    api_key:        apiKey,
    segments,
    avg_calls:      avgCalls,
    avg_cb_rate:    avgCbRate,
    lead_type_dist: leadTypeDist,
  })
  return data.insight
}

export async function getConversionInsights(funnel, sourceStats, modelStats, scoreTiers, apiKey) {
  const { data } = await axios.post('/api/insights/conversion', {
    api_key:      apiKey,
    funnel,
    source_stats: sourceStats,
    model_stats:  modelStats,
    score_tiers:  scoreTiers,
  })
  return data.insight
}
